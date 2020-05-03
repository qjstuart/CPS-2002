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
from openeye import oespicoli

MAX_DIST = 8.0


def main(args):

    if len(args) != 4:
        oechem.OEThrow.Usage("%s <protein> <ligand> <surface>" % args[0])

    pfs = oechem.oemolistream(args[1])
    prot = oechem.OEGraphMol()
    oechem.OEReadMolecule(pfs, prot)
    oechem.OEAssignBondiVdWRadii(prot)

    lfs = oechem.oemolistream(args[2])
    lig = oechem.OEGraphMol()
    oechem.OEReadMolecule(lfs, lig)

    surf = oespicoli.OESurface()
    oespicoli.OEMakeMolecularSurface(surf, prot)

    oespicoli.OESurfaceToMoleculeDistance(surf, lig)

    # Mark the vertices to keep
    for i in range(surf.GetNumVertices()):
        if surf.GetDistanceElement(i) < MAX_DIST:
            surf.SetVertexCliqueElement(i, 1)

    # Crop to the binding site and output
    oespicoli.OESurfaceCropToClique(surf, 1)
    oespicoli.OEWriteSurface(args[3], surf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
