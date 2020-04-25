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
from openeye import oespicoli


def main(args):
    if len(args) != 4:
        oechem.OEThrow.Usage("%s <protein> <ligand> <surface>" % args[0])

    prtfs = oechem.oemolistream(args[1])
    prt = oechem.OEGraphMol()
    oechem.OEReadMolecule(prtfs, prt)
    oechem.OESuppressHydrogens(prt)
    oechem.OEAssignBondiVdWRadii(prt)

    ligfs = oechem.oemolistream(args[2])
    lig = oechem.OEGraphMol()
    oechem.OEReadMolecule(ligfs, lig)
    oechem.OESuppressHydrogens(lig)
    oechem.OEAssignBondiVdWRadii(lig)

    grid = oegrid.OEScalarGrid()
    oespicoli.OEMakeVoidVolume(prt, lig, grid, 0.5)

    surf = oespicoli.OESurface()
    oespicoli.OEMakeSurfaceFromGrid(surf, grid, 0.5)
    oespicoli.OEWriteSurface(args[3], surf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
