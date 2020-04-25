#!/usr/bin/env python
# (C) 2017 OpenEye Scientific Software Inc. All rights reserved.
#
# TERMS FOR USE OF SAMPLE CODE The software below ("Sample Code") is
# provided to current licensees or subscribers of OpenEye products or
# SaaS offerings (each a "Customer").
# Customer is hereby permitted to use, copy, and modify the Sample Code,
# subject to these terms. OpenEye claims no rights to Customer's
# modifications. Modification of Sample Code is at Customer's sole and
# exclusive risk. Sample Code may require Customer to have a then
# current license or subscription to the applicable OpenEye offering.
# THE SAMPLE CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED.  OPENEYE DISCLAIMS ALL WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. In no event shall OpenEye be
# liable for any damages or liability in connection with the Sample Code
# or its use.

from __future__ import print_function
import sys
import os

try:
    from xmlrpclib import ServerProxy, Binary
    from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
except ImportError:  # python 3
    from xmlrpc.client import ServerProxy, Binary
    from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

from threading import Thread
from threading import Lock
from ShapeDatabaseServer import SetupStream

from openeye import oechem

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))


class ShapeServer:
    """ Encapsulates a single ShapeDatabase running on a remote
    server."""

    def __init__(self, servername, querydata, nhits, iformat, oformat, kwargs):
        """ Create a ShapeServer specified by servername and submit
        the querydata query for nhits. """
        self.server = ServerProxy("http://" + servername)
        self.queryidx = self.server.SubmitQuery(querydata, nhits, iformat, oformat, kwargs)

    def QueryStatus(self, blocking):
        """ Return the status of this server. """
        current, total = self.server.QueryStatus(self.queryidx, blocking)

        # only return once the tracer on the server has been initialized
        while total == 0:
            blocking = True
            current, total = self.server.QueryStatus(self.queryidx, blocking)

        return current, total

    def QueryHistogram(self):
        """ Return the histogram from this server. """
        return self.server.QueryHistogram(self.queryidx)

    def QueryResults(self):
        """ Return the results of this server. """
        return self.server.QueryResults(self.queryidx)


class ShapeServerPool:
    """ Abstract a collection of ShapeServer to appear as a single
    server."""

    def __init__(self, servernames, querymolstr, nhits, iformat, oformat, kwargs):
        """ Create a collection of ShapeServers as specified by
        servernames. Launching querymolstr on each for nhits."""
        self.nhits = nhits
        self.oformat = oformat

        thrdpool = LaunchFunctionThreadPool(ShapeServer)

        for sname in servernames:
            thrdpool.AddThread(sname, querymolstr, nhits, iformat, oformat, kwargs)

        self.shapeservers = []
        for server in thrdpool.GetResults():
            self.shapeservers.append(server)

    def QueryStatus(self, blocking):
        """ Return the status of these servers. """
        thrdpool = LaunchFunctionThreadPool(ShapeServer.QueryStatus)

        for server in self.shapeservers:
            thrdpool.AddThread(server, blocking)

        current = 0
        total = 0
        for scur, stot in thrdpool.GetResults():
            sys.stderr.write("%i/%i" % (scur, stot))
            current += scur
            total += stot

        return current, total

    def QueryHistogram(self):
        """ Return the total histogram across all servers. """
        thrdpool = LaunchFunctionThreadPool(ShapeServer.QueryHistogram)

        for server in self.shapeservers:
            thrdpool.AddThread(server)

        totalHist = None
        for hist in thrdpool.GetResults():
            if totalHist is None:
                totalHist = [0] * len(hist)

            totalHist = [lhs + rhs for lhs, rhs in zip(totalHist, hist)]

        return totalHist

    def QueryResults(self):
        """ Return the best nhits results of these servers. """
        timer = oechem.OEWallTimer()
        thrdpool = LaunchFunctionThreadPool(ShapeServer.QueryResults)

        for server in self.shapeservers:
            thrdpool.AddThread(server)

        data = []
        for oebdata in thrdpool.GetResults():
            data.append(oebdata.data)

        sys.stderr.write("%f seconds to get results back" % timer.Elapsed())

        data = b"".join(data)
        if not data:
            sys.stderr.write("Possible query error, no data returned \
                             by any of the downstream servers")
            return ""

        timer.Start()
        # read in from OEB strings
        ifs = oechem.oemolistream()
        ifs = SetupStream(ifs, self.oformat)
        if not ifs.openstring(data):
            sys.stderr.write("Unable to open OEB string from downstream server")
            return ""

        mols = [oechem.OEGraphMol(mol) for mol in ifs.GetOEGraphMols()]

        def GetScoreToCmp(mol):
            if oechem.OEHasSDData(mol, "ShapeTanimoto"):
                # sort by shape tanimoto
                if oechem.OEHasSDData(mol, "TanimotoCombo"):
                    return float(oechem.OEGetSDData(mol, "TanimotoCombo"))
                return float(oechem.OEGetSDData(mol, "ShapeTanimoto"))
            else:
                # sort by shape tversky
                if oechem.OEHasSDData(mol, "TverskyCombo"):
                    return float(oechem.OEGetSDData(mol, "TverskyCombo"))
                return float(oechem.OEGetSDData(mol, "ShapeTversky"))

        mols.sort(key=GetScoreToCmp)
        mols.reverse()

        # write back out to an OEB string
        ofs = oechem.oemolostream()
        ofs = SetupStream(ofs, self.oformat)
        ofs.openstring()

        nhits = self.nhits
        if not nhits:
            nhits = len(mols)

        for mol in mols[:nhits]:
            oechem.OEWriteMolecule(ofs, mol)

        sys.stderr.write("%f seconds to collate hitlist" % timer.Elapsed())

        return Binary(ofs.GetString())


class LaunchFunctionThread(Thread):
    """ A thread to launch a function and be able to retrieve its
    return value."""

    def __init__(self, func, *args):
        Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception as e:
            self.exception = e

    def GetResult(self):
        if hasattr(self, "exception"):
            raise self.exception
        return self.result


class LaunchFunctionThreadPool:
    """ Given a function, launch it in several threads with a separate
    argument list for each."""

    def __init__(self, func):
        """ Start a new thread pool to execute the function func. """
        self.func = func
        self.threads = []

    def AddThread(self, *args):
        """ Create and start another thread to run func on args. """
        thrd = LaunchFunctionThread(self.func, *args)
        thrd.start()
        self.threads.append(thrd)

    def GetResults(self):
        """ Returns an iterable of the results of each thread in the
        order they were added with AddThread."""
        for thrd in self.threads:
            thrd.join()
            yield thrd.GetResult()


def ShapeServerIsLoaded(servername, blocking):
    """ Helper function to determine whether a server is in the 'loaded' state. """
    server = ServerProxy("http://" + servername)
    return server.IsLoaded(blocking)


class ShapeServerProxy:
    """ Proxy queries across multiple remote shape servers."""

    def __init__(self, servernames):
        """ Create a proxy  """
        self.servernames = servernames
        self.queryidx = 0
        self.activequeries = {}
        self.lock = Lock()

    def IsLoaded(self, blocking=False):
        """ Return whether the servers have finished loading. """
        thrdpool = LaunchFunctionThreadPool(ShapeServerIsLoaded)

        for server in self.servernames:
            thrdpool.AddThread(server, blocking)

        areloaded = True
        for result in thrdpool.GetResults():
            areloaded = areloaded and result

        return areloaded

    def SubmitQuery(self, querymolstr, nhits, iformat=".oeb", oformat=".oeb", kwargs=None):
        """ Submit a query to these shape servers. """
        if not kwargs:
            kwargs = {}
        shapeservers = ShapeServerPool(self.servernames, querymolstr,
                                       nhits, iformat, oformat, kwargs)

        self.lock.acquire()
        try:
            idx = self.queryidx
            self.queryidx += 1

            self.activequeries[idx] = shapeservers
        finally:
            self.lock.release()

        return idx

    def QueryStatus(self, queryidx, blocking=False):
        """ Return the status of the query specified by queryidx. """
        self.lock.acquire()
        try:
            shapeservers = self.activequeries[queryidx]
        finally:
            self.lock.release()

        return shapeservers.QueryStatus(blocking)

    def QueryHistogram(self, queryidx):
        """ Return the current histogram of scores specified by
        queryidx."""
        self.lock.acquire()
        try:
            shapeservers = self.activequeries[queryidx]
        finally:
            self.lock.release()

        return shapeservers.QueryHistogram()

    def QueryResults(self, queryidx):
        """ Return the results of the query specified by queryidx. """
        self.lock.acquire()
        try:
            shapeservers = self.activequeries.pop(queryidx)
        finally:
            self.lock.release()

        return shapeservers.QueryResults()


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def main(argv=[__name__]):
    if len(argv) < 2:
        oechem.OEThrow.Usage("%s <server 1> <server 2> ... <server n> [portnumber=8080]" % argv[0])

    # default port number is 8080
    portnumber = 8080
    try:
        portnumber = int(argv[-1])
        servernames = argv[1:-1]
    except ValueError:
        servernames = argv[1:]

    # Create server, an empty string is used to allow connections with
    # any hostname
    server = SimpleXMLRPCServer(("", portnumber),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_instance(ShapeServerProxy(servernames))

    try:
        # Run the server's main loop
        server.serve_forever()
    finally:
        server.server_close()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
