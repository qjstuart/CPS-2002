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
from openeye import oezap


def main(argv=[__name__]):
    itf = oechem.OEInterface()
    if not SetupInterface(argv, itf):
        return 1

    zap = oezap.OEZap()
    zap.SetInnerDielectric(itf.GetFloat("-epsin"))
    zap.SetOuterDielectric(itf.GetFloat("-epsout"))
    zap.SetGridSpacing(itf.GetFloat("-grid_spacing"))
    zap.SetBoundarySpacing(itf.GetFloat("-buffer"))

    mol = oechem.OEGraphMol()
    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))
    oechem.OEReadMolecule(ifs, mol)
    oechem.OEAssignBondiVdWRadii(mol)
    oechem.OEMMFFAtomTypes(mol)
    oechem.OEMMFF94PartialCharges(mol)

    zap.SetMolecule(mol)

    grid = oegrid.OEScalarGrid()
    if zap.CalcPotentialGrid(grid):
        if itf.GetBool("-mask"):
            oegrid.OEMaskGridByMolecule(grid, mol)
        oegrid.OEWriteGrid(itf.GetString("-out"), grid)
    return 0


InterfaceData = """
#zap_grid2 interface definition

!PARAMETER -in
  !TYPE string
  !BRIEF Input molecule file
  !REQUIRED true
!END

!PARAMETER -out
  !TYPE string
  !BRIEF Output grid file
  !REQUIRED true
!END

!PARAMETER -epsin
  !TYPE float
  !BRIEF Inner dielectric
  !DEFAULT 1.0
  !LEGAL_RANGE 0.0 100.0
!END

!PARAMETER -epsout
  !TYPE float
  !BRIEF Outer dielectric
  !DEFAULT 80.0
  !LEGAL_RANGE 0.0 100.0
!END

!PARAMETER -grid_spacing
  !TYPE float
  !DEFAULT 0.5
  !BRIEF Spacing between grid points (Angstroms)
  !LEGAL_RANGE 0.1 2.0
!END

!PARAMETER -buffer
  !TYPE float
  !DEFAULT 2.0
  !BRIEF Extra buffer outside extents of molecule.
  !LEGAL_RANGE 0.1 10.0
!END

!PARAMETER -mask
  !TYPE bool
  !DEFAULT false
  !BRIEF Mask potential grid by the molecule
!END
"""


def SetupInterface(argv, itf):
    oechem.OEConfigure(itf, InterfaceData)
    if oechem.OECheckHelp(itf, argv):
        return False
    if not oechem.OEParseCommandLine(itf, argv):
        return False
    infile = itf.GetString("-in")
    if not oechem.OEIsReadable(oechem.OEGetFileType(oechem.OEGetFileExtension(infile))):
        oechem.OEThrow.Warning("%s is not a readable input file" % infile)
        return False
    outfile = itf.GetString("-out")
    if not oegrid.OEIsWriteableGrid(oegrid.OEGetGridFileType(oechem.OEGetFileExtension(outfile))):
        oechem.OEThrow.Warning("%s is not a writable grid file" % outfile)
        return False
    return True


if __name__ == "__main__":
    sys.exit(main(sys.argv))
