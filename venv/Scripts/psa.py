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

from __future__ import print_function
import sys

from openeye import oechem
from openeye import oespicoli


def MakeCliques(surf, mol):
    for i in range(surf.GetNumVertices()):
        atom = mol.GetAtom(oechem.OEHasAtomIdx(surf.GetAtomsElement(i)))
        if atom.IsOxygen() or atom.IsNitrogen() or atom.IsPolarHydrogen():
            surf.SetVertexCliqueElement(i, 1)
            surf.SetColorElement(i, 0.0, 0.0, 1.0)
        else:
            surf.SetColorElement(i, 1.0, 0.0, 0.0)
    return True


def AverageSurfaceArea(mcmol):
    area = 0.0
    parea = 0.0
    for conf in mcmol.GetConfs():
        surf = oespicoli.OESurface()
        oespicoli.OEMakeMolecularSurface(surf, conf, 0.5)
        MakeCliques(surf, conf)
        area += oespicoli.OESurfaceArea(surf)
        parea += oespicoli.OESurfaceCliqueArea(surf, 1)
    area /= mcmol.NumConfs()
    parea /= mcmol.NumConfs()
    return area, parea


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <molfile>" % argv[0])

    ifs = oechem.oemolistream(argv[1])
    for mol in ifs.GetOEMols():
        oechem.OEAssignBondiVdWRadii(mol)
        area, polararea = AverageSurfaceArea(mol)
        print(mol.GetTitle())
        print("molecule has %d conformers" % mol.NumConfs())
        print("Average total surface area: %f" % area)
        print("Average polar area        : %f" % polararea)
        print("Average %% polar          : %f" % ((polararea/area) * 100))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
