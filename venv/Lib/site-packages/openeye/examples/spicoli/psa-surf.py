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


def ColorSurface(surf, mol):

    for i in range(surf.GetNumVertices()):
        atom = mol.GetAtom(oechem.OEHasAtomIdx(surf.GetAtomsElement(i)))
        if (atom.IsOxygen() or atom.IsNitrogen() or atom.IsPolarHydrogen()):
            surf.SetColorElement(i, 0.0, 0.0, 1.0)
        else:
            surf.SetColorElement(i, 1.0, 0.0, 0.0)

    return True


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <molecules> <oebfile>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[2])

    for mol in ifs.GetOEGraphMols():
        oechem.OEAssignBondiVdWRadii(mol)

        surf = oespicoli.OESurface()
        oespicoli.OEMakeMolecularSurface(surf, mol, 0.5)
        ColorSurface(surf, mol)
        mol.SetData("psasurf", surf)

        oechem.OEWriteMolecule(ofs, mol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
