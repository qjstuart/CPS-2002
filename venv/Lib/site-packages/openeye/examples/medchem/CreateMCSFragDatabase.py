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

#############################################################################
# Utility to perform an MCS fragmentation on an input set of structures
#  and save the index for subsequent analysis
# ---------------------------------------------------------------------------
# CreateMCSFragDatabase index_mols output_index
#                       [ -verbose 1 ]  // optional verbosity
#
# index_mols: filename of input molecules to analyze
# output_index: filename of MCS fragment index
#############################################################################
from __future__ import print_function

from openeye import oechem
from openeye import oemedchem
import sys


def MCSFragIndex(itf):
    # output index file
    mcsindexfile = itf.GetString("-output")
    if not oemedchem.OEIsMCSFragDatabaseFileType(mcsindexfile):
        oechem.OEThrow.Fatal("Output file is not an mcs fragment index type \
                             - needs .mcsfrag extension: {}" .format(mcsindexfile))

    # create options class with defaults
    mcsopt = oemedchem.OEMCSFragDatabaseOptions()
    # set up options from command line
    if not oemedchem.OESetupMCSFragDatabaseOptions(mcsopt, itf):
        oechem.OEThrow.Fatal("Error setting MCS fragment database options")

    # input structures to index
    ifsindex = oechem.oemolistream()
    if not ifsindex.open(itf.GetString("-input")):
        oechem.OEThrow.Fatal("Unable to open {} for reading"
                             .format(itf.GetString("-input")))

    # get requested verbosity setting
    verbose = itf.GetBool("-verbose")
    timer = itf.GetBool("-timer")
    if verbose:
        timer = True

    watch = oechem.OEStopwatch()

    maxrec = max(itf.GetInt("-maxrec"), 0)
    statusrec = itf.GetInt("-status")

    if verbose:
        if not mcsopt.HasIndexableFragmentHeavyAtomRange():
            oechem.OEThrow.Info("Indexing all fragments")
        else:
            oechem.OEThrow.Info("Using index range={0:.1f}-{1:.1f}%"
                                .format(mcsopt.GetIndexableFragmentRangeMin(),
                                        mcsopt.GetIndexableFragmentRangeMax()))
        if statusrec:
            oechem.OEThrow.Info("Status output after every {0} records".format(statusrec))
        if maxrec:
            oechem.OEThrow.Info("Indexing a maximum of {0} records".format(maxrec))

    # create indexing engine
    mcsdb = oemedchem.OEMCSFragDatabase(mcsopt)

    # add molecules to be indexed
    record = 0
    unindexed = 0
    for mol in ifsindex.GetOEGraphMols():
        status = mcsdb.AddMol(mol, record)
        if status != record:
            unindexed += 1
            if verbose:
                oechem.OEThrow.Info('Input structure not added to index, record=%d status=%s' %
                                    (record, oemedchem.OEMatchedPairIndexStatusName(status)))
        record += 1
        if maxrec and record >= maxrec:
            break  # maximum record limit reached
        if statusrec and (record % statusrec) == 0:
            oechem.OEThrow.Info("Records: {} Indexed: {} Unindexed: {}"
                                .format(record, (record - unindexed), unindexed))

    indextime = watch.Elapsed()
    if record == 0:
        oechem.OEThrow.Fatal("No records in input structure file for indexing")

    if not mcsdb.NumFragments():
        oechem.OEThrow.Fatal('No fragments found from indexing, ' +
                             'use -fragGe,-fragLe options to extend indexing range')

    if timer:
        if (not verbose and not timer) or not indextime:
            oechem.OEThrow.Fatal("Processed {0} molecules, "
                                 "generating {1} fragments"
                                 .format(record, mcsdb.NumFragments()))
        else:
            oechem.OEThrow.Info("Processed {0} molecules, "
                                "generating {1} fragments in {2:.2F} sec: "
                                "{3:,.1F} mols/sec {4:,.1F} frags/sec"
                                .format(record,
                                        mcsdb.NumFragments(),
                                        indextime,
                                        float(record)/float(indextime),
                                        float(mcsdb.NumFragments())/float(indextime)))

    if not oemedchem.OEWriteMCSFragDatabase(mcsindexfile, mcsdb):
        oechem.OEThrow.Fatal("Error serializing MCS fragment database: {}"
                             .format(mcsindexfile))

    # return some status information
    oechem.OEThrow.Info("Records: {}, Indexed: {}, fragments: {:,d}"
                        .format(record,
                                mcsdb.NumMols(),
                                mcsdb.NumFragments()))
    return 0


############################################################
InterfaceData = """
#createmcsfragdatabase interface file
!CATEGORY CreateMCSFragDatabase

    !CATEGORY I/O
        !PARAMETER -input 1
          !TYPE string
          !REQUIRED true
          !BRIEF Input filename of structure(s) to index
          !KEYLESS 1
        !END

        !PARAMETER -output 2
          !TYPE string
          !REQUIRED true
          !BRIEF Output filename of MCS fragment serialized index
          !KEYLESS 2
        !END

    !END

    !CATEGORY options
        !PARAMETER -verbose 1
           !TYPE bool
           !DEFAULT 0
           !BRIEF generate verbose output
        !END
        !PARAMETER -maxrec 2
           !TYPE int
           !DEFAULT 0
           !BRIEF limit indexing to -maxrec records from the -input structures
        !END
        !PARAMETER -timer 3
           !TYPE bool
           !DEFAULT 0
           !BRIEF report indexing time
        !END
        !PARAMETER -status 4
           !TYPE int
           !DEFAULT 0
           !BRIEF print indexing status every -status records
        !END
    !END
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    oemedchem.OEConfigureMCSFragDatabaseOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    MCSFragIndex(itf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
