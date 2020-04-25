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


# Format of ANISOU record: http://www.ccp4.ac.uk/html/pdbformat.html#part1ani
def ParseFactors(line):
    factors = []
    cols = list(range(28, 71, 7))
    prev = cols.pop(0)
    while cols:
        next = cols.pop(0)
        factors.append(float(line[prev:next])/10000.0)
        prev = next
    return int(line[6:11]), factors


def GetEllipsoidalSurface(center, factors):
    surf = oespicoli.OESurface()
    dir1 = oechem.OEFloatArray(3)
    dir1[0] = factors[0]
    dir1[1] = factors[3]
    dir1[2] = factors[4]
    dir2 = oechem.OEFloatArray(3)
    dir2[0] = factors[3]
    dir2[1] = factors[1]
    dir2[2] = factors[5]
    dir3 = oechem.OEFloatArray(3)
    dir3[0] = factors[4]
    dir3[1] = factors[5]
    dir3[2] = factors[2]
    oespicoli.OEMakeEllipsoidSurface(surf, center, 10.0, 10.0, 10.0, dir1, dir2, dir3, 4)
    return surf


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <molfile.pdb> <out.srf>" % argv[0])

    mol = oechem.OEGraphMol()
    ifs = oechem.oemolistream(argv[1])
    oechem.OEReadMolecule(ifs, mol)
    if not oechem.OEHasResidues(mol):
        oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)

    serials = {}
    for atom in mol.GetAtoms():
        res = oechem.OEAtomGetResidue(atom)
        serials[res.GetSerialNumber()] = atom

    outsurf = oespicoli.OESurface()
    center = oechem.OEFloatArray(3)
    for line in open(argv[1]):
        if line.startswith("ANISOU"):
            serno, factors = ParseFactors(line)
            if serno in serials:
                mol.GetCoords(serials[serno], center)
                surf = GetEllipsoidalSurface(center, factors)
                oespicoli.OEAddSurfaces(outsurf, surf)

    oespicoli.OEWriteSurface(argv[2], outsurf)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
