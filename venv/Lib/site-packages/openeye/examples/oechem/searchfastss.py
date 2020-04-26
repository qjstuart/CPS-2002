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
# Performs SMARTS search on substructure database file
#############################################################################
import sys
from openeye import oechem


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line.")

    # check parameters

    c = itf.GetBool("-count")
    t = itf.GetBool("-titles")
    o = itf.HasString("-out")

    if not((c and not t and not o) or (not c and t and not o) or (not c and not t and o)):
        oechem.OEThrow.Fatal("Counting (-c) or outputting titles (-t) or molecules (-o) "
                             "must be specified and are mutually exclusive.")

    ofs = oechem.oemolostream()
    if itf.HasString("-out"):
        ofname = itf.GetString("-out")
        if not ofs.open(ofname):
            oechem.OEThrow.Fatal("Cannot open output file!")

    dbfname = itf.GetString("-db")
    smarts = itf.GetString("-smarts")
    nrthreads = itf.GetUnsignedInt("-nrthreads")
    maxmatches = itf.GetUnsignedInt("-maxmatches")

    # initialize query

    qmol = oechem.OEQMol()
    if not oechem.OEParseSmarts(qmol, smarts):
        oechem.OEThrow.Fatal("Unable to parse SMARTS pattern: %s" % smarts)

    # initialize substructure search database

    screentype = oechem.OEGetSubSearchScreenType(oechem.OESubSearchScreenType_SMARTS)

    if not oechem.OEIsValidSubSearchDatabase(dbfname, screentype):
        oechem.OEThrow.Fatal("Invalid SMARTS substructure search database file!")

    ssdb = oechem.OESubSearchDatabase(oechem.OESubSearchDatabaseType_Default, nrthreads)
    tracer = oechem.OEConsoleProgressTracer()
    if not ssdb.Open(dbfname, tracer):
        oechem.OEThrow.Fatal("Substructure search database can not be initialized!")

    screenstr = screentype.GetName()
    infomsg = "Using %d processor(s) to search database with '%s'"
    oechem.OEThrow.Info(infomsg % (ssdb.NumProcessors(), screenstr))

    # search database

    if itf.GetBool("-count"):
        oechem.OEThrow.Info("Number of hits: %d" % ssdb.NumMatches(qmol))
    else:
        query = oechem.OESubSearchQuery(qmol, maxmatches)
        result = oechem.OESubSearchResult()
        status = ssdb.Search(result, query)

        print("Search status = ", oechem.OESubSearchStatusToName(status))

        print("Number of targets  = ", result.NumTargets())
        print("Number of screened = ", result.NumScreened())
        print("Number of searched = ", result.NumSearched())
        print("Number of total matches = ", result.NumTotalMatches())
        print("Number of kept  matches = ", result.NumMatches())

        if itf.GetBool("-titles"):
            print("Matches:")
            for index in result.GetMatchIndices():
                print(ssdb.GetTitle(index))

        elif itf.HasString("-out"):
            mol = oechem.OEGraphMol()
            for index in result.GetMatchIndices():
                if ssdb.GetMolecule(mol, index):
                    oechem.OEWriteMolecule(ofs, mol)

    return 0

#############################################################################


InterfaceData = """\
!BRIEF [options] -db <database> -s <smarts> -nrthreads <unsigned int>

!CATEGORY "input/output options"

  !PARAMETER -database 1
    !ALIAS -db
    !TYPE string
    !REQUIRED true
    !VISIBILITY simple
    !BRIEF Input substructure search database filename
  !END

  !PARAMETER -smarts 2
    !ALIAS -s
    !TYPE string
    !REQUIRED true
    !BRIEF SMARTS pattern, quote for safety
  !END

!END

!CATEGORY "search types"

  !PARAMETER -count
    !ALIAS -c
    !TYPE bool
    !DEFAULT false
    !BRIEF Output count of number matched
  !END

  !PARAMETER -titles
    !ALIAS -t
    !TYPE bool
    !DEFAULT false
    !BRIEF Output title of matches
  !END

  !PARAMETER -out
    !ALIAS -o
    !TYPE string
    !BRIEF Output molecule filename of matches
  !END

!END

!CATEGORY "other options"

  !PARAMETER -nrthreads
    !TYPE unsigned
    !REQUIRED  true
    !DEFAULT 1
    !BRIEF  Number of processors used (zero means all available)
  !END

  !PARAMETER -maxmatches
    !ALIAS -max
    !TYPE unsigned
    !DEFAULT 1000
    !BRIEF The maximum number of matches returned in case of parameters (-titles) and (-out)
  !END

!END
"""

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
