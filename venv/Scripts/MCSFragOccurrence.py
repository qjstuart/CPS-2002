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

###############################################################################
# report common fragments from an input set of molecules
###############################################################################
from __future__ import print_function
from openeye import oechem
from openeye import oemedchem

import operator
import sys


def MCSFragOccurrence(itf):

    verbose = itf.GetBool("-verbose")
    timer = itf.GetBool("-timer")

    indb = itf.GetString("-indb")
    if not oemedchem.OEIsMCSFragDatabaseFileType(indb):
        oechem.OEThrow.Fatal("Option -indb must specify a .mcsfrag filename: "
                             + indb)
    if verbose:
        oechem.OEThrow.Info("Loading index from " + indb)

    watch = oechem.OEStopwatch()
    watch.Start()
    mcsdb = oemedchem.OEMCSFragDatabase()
    if not oemedchem.OEReadMCSFragDatabase(indb, mcsdb):
        oechem.OEThrow.Fatal("Error deserializing MCS fragment database: "
                             + indb)
    loadtime = watch.Elapsed()

    if not mcsdb.NumMols():
        oechem.OEThrow.Fatal("Loaded empty index")

    if not timer or not loadtime:
        oechem.OEThrow.Info("Loaded index of {0} molecules, {1} fragments"
                            .format(mcsdb.NumMols(), mcsdb.NumFragments()))
    else:
        oechem.OEThrow.Info("Loaded index of {0} molecules, {1} "
                            "fragments in {2:.2F} sec: "
                            "{3:,.1F} mols/sec {4:,.1F} frags/sec"
                            .format(mcsdb.NumMols(),
                                    mcsdb.NumFragments(),
                                    loadtime,
                                    float(mcsdb.NumMols())/loadtime,
                                    float(mcsdb.NumFragments())/loadtime))

    if not mcsdb.NumFragments():
        oechem.OEThrow.Fatal("No fragments loaded from index, "
                             "use -fragGe,-fragLe options to "
                             "extend indexable range")

    queryfile = itf.GetString("-query")
    ifsquery = oechem.oemolistream()
    if not ifsquery.open(queryfile):
        oechem.OEThrow.Fatal("Unable to open query file: " + queryfile)

    # process the query options
    qmaxrec = 0
    if itf.HasInt("-qlim"):
        qmaxrec = itf.GetInt("-qlim")

    record = 0
    uniqueCores = set()
    qmol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifsquery, qmol):
        cores = mcsdb.MoleculeToCores(qmol)
        for core in cores:
            # collect unique cores with >0 counts in the index
            if not mcsdb.CoreToMoleculeCount(core):
                continue
            uniqueCores.add(core)
        record += 1
        if qmaxrec and record >= qmaxrec:
            break

    coreOcc = dict()
    for core in uniqueCores:
        coreOcc[core] = mcsdb.CoreToMoleculeCount(core)

    oechem.OEThrow.Info('Common fragments with occurrence >1:')
    num = 0
    topnum = itf.GetInt('-top')
    for k, v in sorted(coreOcc.items(),
                       key=operator.itemgetter(1, 0),
                       reverse=True):
        if v <= 1:
            break
        num += 1
        ids = list(mcsdb.CoreToMolecules(k))
        oechem.OEThrow.Info('{} {} {}'.format(v, k, ids))
        if topnum and num >= topnum:
            break

    if itf.GetBool('-uncommon'):
        oechem.OEThrow.Info('Uncommon fragments:')
        for k, v in sorted(coreOcc.items(),
                           key=operator.itemgetter(1)):
            if v > 1:
                break
            ids = list(mcsdb.CoreToMolecules(k))
            oechem.OEThrow.Info('{} {} {}'.format(v, k, ids))


############################################################
InterfaceData = """
#MCSFragOccurrence interface file
!CATEGORY MCSFragOccurrence

    !CATEGORY I/O
        !PARAMETER -indb 1
          !TYPE string
          !REQUIRED true
          !BRIEF Input filename of index file to load
          !KEYLESS 1
        !END

        !PARAMETER -query 2
          !TYPE string
          !REQUIRED true
          !BRIEF query structure file to report cores against
          !KEYLESS 2
        !END
    !END

    !CATEGORY options
        !PARAMETER -verbose 1
           !TYPE bool
           !DEFAULT 0
           !BRIEF generate verbose output
        !END
        !PARAMETER -timer 2
           !TYPE bool
           !DEFAULT 0
           !BRIEF report database loading time
        !END
        !PARAMETER -top 3
           !TYPE int
           !DEFAULT 10
           !LEGAL_RANGE 0 inf
           !BRIEF print the -top number of common fragment occurrences (0:all, 10:default)
        !END
        !PARAMETER -uncommon 4
           !TYPE bool
           !DEFAULT 0
           !BRIEF print the uncommon fragments also
        !END
        !PARAMETER -qlim 5
           !TYPE int
           !DEFAULT 0
           !BRIEF limit query processing to -qlim records from the -query structures
        !END
    !END
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    MCSFragOccurrence(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
