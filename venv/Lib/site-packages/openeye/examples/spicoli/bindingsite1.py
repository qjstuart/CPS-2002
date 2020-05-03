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


def GetDist2(acoords, vcoords):
    d2 = (vcoords[0]-acoords[0]) * (vcoords[0]-acoords[0])
    d2 += (vcoords[1]-acoords[1]) * (vcoords[1]-acoords[1])
    d2 += (vcoords[2]-acoords[2]) * (vcoords[2]-acoords[2])
    return d2


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

    # Iterate through all the protein surface vertices
    for i in range(surf.GetNumVertices()):
        vert = surf.GetVertex(i)

        # Check the distance to each atom
        for atom in lig.GetAtoms():
            dist2 = GetDist2(lig.GetCoords(atom), vert)
            if dist2 < MAX_DIST*MAX_DIST:
                surf.SetVertexCliqueElement(i, 1)

    # Crop to the binding site and output
    oespicoli.OESurfaceCropToClique(surf, 1)
    oespicoli.OEWriteSurface(args[3], surf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
