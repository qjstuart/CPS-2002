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
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <molfile>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    mol = oechem.OEGraphMol()

    oechem.OEReadMolecule(ifs, mol)
    oechem.OEAssignBondiVdWRadii(mol)
    oechem.OEMMFFAtomTypes(mol)
    oechem.OEMMFF94PartialCharges(mol)

    zap = oezap.OEZap()
    zap.SetInnerDielectric(1.0)
    zap.SetGridSpacing(0.5)
    zap.SetMolecule(mol)

    # calculate standard 2-dielectric grid
    grid1 = oegrid.OEScalarGrid()
    zap.CalcPotentialGrid(grid1)

    # calculate grid with single dielectric
    grid2 = oegrid.OEScalarGrid()
    zap.SetOuterDielectric(zap.GetInnerDielectric())
    zap.CalcPotentialGrid(grid2)

    # take the difference
    oegrid.OESubtractScalarGrid(grid1, grid2)

    # mask out everything outside the molecule
    oegrid.OEMaskGridByMolecule(grid1, mol, oegrid.OEGridMaskType_GaussianMinus)

    oegrid.OEWriteGrid("zap_diff.grd", grid1)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
