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
# Generates database for fast substructure search.
#############################################################################
import sys
from openeye import oechem


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line.")

    ifname = itf.GetString("-in")
    ofname = itf.GetString("-out")
    stype = itf.GetString("-stype")
    sort = itf.GetBool("-sort")
    keeptitle = itf.GetBool("-keep-title")
    nrthreads = itf.GetUnsignedInt("-nrthreads")

    screentype = None
    if stype == "MOLECULE":
        screentype = oechem.OEGetSubSearchScreenType(oechem.OESubSearchScreenType_Molecule)
    elif stype == "MDL":
        screentype = oechem.OEGetSubSearchScreenType(oechem.OESubSearchScreenType_MDL)
    elif stype == "SMARTS":
        screentype = oechem.OEGetSubSearchScreenType(oechem.OESubSearchScreenType_SMARTS)
    if screentype is None:
        oechem.OEThrow.Fatal("stype %s is not supported" % stype)

    opts = oechem.OECreateSubSearchDatabaseOptions(screentype)
    opts.SetSortByBitCounts(sort)
    opts.SetKeepTitle(keeptitle)
    opts.SetNumProcessors(nrthreads)

    screenstr = screentype.GetName()
    infomsg = "Using %d processor(s) to generate database with '%s'"
    oechem.OEThrow.Info(infomsg % (opts.GetNumProcessors(), screenstr))

    tracer = oechem.OEConsoleProgressTracer()
    if not oechem.OECreateSubSearchDatabaseFile(ofname, ifname, opts, tracer):
        oechem.OEThrow.Fatal("Substructure search database can not be generated!")

    return 0

#############################################################################


InterfaceData = """\
!BRIEF [options] -in <input> -out <output> -stype <screentype>

!CATEGORY "input/output options"

  !PARAMETER -in 1
    !ALIAS -i
    !TYPE string
    !REQUIRED true
    !VISIBILITY simple
    !BRIEF Input molecule filename
  !END

  !PARAMETER -out 2
    !ALIAS -o
    !TYPE string
    !REQUIRED true
    !VISIBILITY simple
    !BRIEF Output substructure database filename
  !END

!END

!CATEGORY "other options"

  !PARAMETER -screentype
    !ALIAS -stype
    !TYPE string
    !REQUIRED  true
    !LEGAL_VALUE MOLECULE
    !LEGAL_VALUE MDL
    !LEGAL_VALUE SMARTS
    !BRIEF Screen type generated
  !END

  !PARAMETER -nrthreads
    !TYPE unsigned
    !DEFAULT 0
    !BRIEF  Number of processors used (zero means all available)
    !DETAIL
  !END

  !PARAMETER -sort
    !TYPE bool
    !DEFAULT true
    !BRIEF  Whether to sort the molecules based on their screen bit counts.
    !DETAIL
        Generating sorted databases can be slower, but searching them will
        be faster.
  !END

  !PARAMETER -keep-title
    !TYPE bool
    !DEFAULT true
    !BRIEF  Whether to keep the title of the molecule as unique identifier
    !DETAIL
        If false, then a 16 character long unique identifier will be generated
        for each molecule as a new title.
  !END

!END
"""

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
