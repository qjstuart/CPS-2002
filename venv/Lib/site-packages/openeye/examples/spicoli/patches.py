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


def AtomInHydrophobicResidue(atom):
    residues = set([oechem.OEResidueIndex_ALA,
                    oechem.OEResidueIndex_ILE,
                    oechem.OEResidueIndex_LEU,
                    oechem.OEResidueIndex_MET,
                    oechem.OEResidueIndex_PHE,
                    oechem.OEResidueIndex_PRO,
                    oechem.OEResidueIndex_TRP,
                    oechem.OEResidueIndex_VAL])

    if oechem.OEGetResidueIndex(atom) in residues:
        return True
    else:
        return False


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <protein> <surface>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    mol = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, mol)
    oechem.OEPerceiveResidues(mol)
    oechem.OEAssignBondiVdWRadii(mol)

    # Generate the molecular surface
    surf = oespicoli.OESurface()
    oespicoli.OEMakeMolecularSurface(surf, mol, 0.5)

    # Mark all the vertices associated with hydrophobic atoms
    for i in range(surf.GetNumVertices()):
        atom = mol.GetAtom(oechem.OEHasAtomIdx(surf.GetAtomsElement(i)))
        if (AtomInHydrophobicResidue(atom)):
            surf.SetVertexCliqueElement(i, 1)

    # Crop to only those triangles
    oespicoli.OESurfaceCropToClique(surf, 1)

    # nlqs is the number of different connected components
    nclqs = oespicoli.OEMakeConnectedSurfaceCliques(surf)

    # Find the largest component
    maxclq = 0
    maxarea = 0.0
    for i in range(nclqs):
        area = oespicoli.OESurfaceCliqueArea(surf, i+1)
        print("clique: %d  area: %f" % (i+1, area))
        if (area > maxarea):
            maxclq = i+1
            maxarea = area

    # Crop to it
    oespicoli.OESurfaceCropToClique(surf, maxclq)

    oespicoli.OEWriteSurface(args[2], surf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
