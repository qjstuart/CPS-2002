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
import os
import sys
import socket

try:
    from xmlrpclib import ServerProxy
except ImportError:  # python 3
    from xmlrpc.client import ServerProxy

from time import sleep

from openeye import oechem

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))

InterfaceData = """\
!BRIEF [-blocking] [-h] <server:port>
!PARAMETER -host
  !ALIAS -h
  !TYPE string
  !REQUIRED true
  !BRIEF The host to check to see if it is up yet
  !KEYLESS 1
!END
!PARAMETER -blocking
  !ALIAS -b
  !TYPE bool
  !DEFAULT false
  !BRIEF If true the program will not exit until the database has finished loading.
!END
!PARAMETER -retries
  !ALIAS -r
  !TYPE int
  !DEFAULT 10
  !BRIEF Number of times to try connecting to the server.
!END
!PARAMETER -timeout
  !ALIAS -t
  !TYPE float
  !DEFAULT 60.0
  !BRIEF The time between retries is the timeout divided by the number of retries.
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    host = itf.GetString("-host")
    s = ServerProxy("http://" + host)

    blocking = itf.GetBool("-blocking")
    retries = itf.GetInt("-retries")
    if retries < 1:
        oechem.OEThrow.Fatal("-retries must be greater than 0")
    timeout = itf.GetFloat("-timeout")
    if timeout <= 0.0:
        oechem.OEThrow.Fatal("-timeout must be greater than 0.0")
    waittime = timeout/retries
    loaded = False
    while retries:
        try:
            loaded = s.IsLoaded(blocking)
            break
        except socket.error:
            retries -= 1
            if retries:
                print("Unable to connect to %s, retrying in %2.1f seconds" % (host, waittime))
                sleep(waittime)

    if not retries:
        print("Was never able to connect to a server, exiting...")
        return -1

    if loaded:
        loaded = "True"
    else:
        loaded = "False"

    print(host, "IsLoaded =", loaded)

    if loaded:
        return 0

    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
