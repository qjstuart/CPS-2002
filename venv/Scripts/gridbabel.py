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


import sys
from openeye import oechem
from openeye import oegrid


def SetupInterface(itf, argv):
    if not oechem.OEConfigure(itf, InterfaceData):
        return False

    if oechem.OECheckHelp(itf, argv):
        return False

    return oechem.OEParseCommandLine(itf, argv)


def main(argv=[__name__]):
    itf = oechem.OEInterface()
    if not SetupInterface(itf, argv):
        return 1

    res = itf.GetFloat("-res")

    regularize = itf.GetBool("-regularize")

    outfile = itf.GetString("-o")
    if not oegrid.OEIsWriteableGrid(oegrid.OEGetGridFileType(oechem.OEGetFileExtension(outfile))):
        oechem.OEThrow.Fatal("Not a writeable grid file: %s" % outfile)

    infile = itf.GetString("-i")

    if oegrid.OEIsReadableGrid(oegrid.OEGetGridFileType(oechem.OEGetFileExtension(infile))):
        if (regularize):
            grid = oegrid.OEScalarGrid()
        else:
            grid = oegrid.OESkewGrid()

        if oegrid.OEReadGrid(infile, grid):
            oegrid.OEWriteGrid(outfile, grid)
        else:
            oechem.OEThrow.Fatal("Problem reading grid file: %s" % infile)
    elif oechem.OEIsReadable(oechem.OEGetFileType(oechem.OEGetFileExtension(infile))):
        ifs = oechem.oemolistream(infile)
        mol = oechem.OEMol()
        if oechem.OEReadMolecule(ifs, mol):
            oechem.OEAssignBondiVdWRadii(mol)
            grid = oegrid.OEScalarGrid()
            oegrid.OEMakeMolecularGaussianGrid(grid, mol, res)
            oegrid.OEWriteGrid(outfile, grid)
        else:
            oechem.OEThrow.Fatal("Problem reading molecule file: %s" % infile)
    else:
        oechem.OEThrow.Fatal("Not a readable grid file: %s", infile)

    oechem.OEThrow.Info("Converted %s into %s" % (infile, outfile))

    return 0


InterfaceData = """
# gridbabel

!PARAMETER -i
  !TYPE string
  !REQUIRED true
  !KEYLESS 1
  !BRIEF input filename
!END

!PARAMETER -o
  !TYPE string
  !REQUIRED true
  !KEYLESS 2
  !BRIEF output filename
!END

!PARAMETER -res
  !TYPE float
  !REQUIRED false
  !DEFAULT 0.5
  !LEGAL_RANGE 0.1 4.0
!END

!PARAMETER -regularize
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
