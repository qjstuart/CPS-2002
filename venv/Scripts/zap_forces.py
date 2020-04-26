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
from openeye import oezap


def PrintHeader(title):
    oechem.OEThrow.Info("\nForce Components for %s, in kT/Angstrom" % title)
    oechem.OEThrow.Info("%6s %8s %8s %8s %8s" % ("Index", "Element", "-dE/dx",
                                                 "-dE/dy", "-dE/dz"))


def PrintForces(mol, forces):
    for atom in mol.GetAtoms():
        oechem.OEThrow.Info("%6d %8s %8.2f %8.2f %8.2f" %
                            (atom.GetIdx(),
                             oechem.OEGetAtomicSymbol(atom.GetAtomicNum()),
                             forces[atom.GetIdx()],
                             forces[atom.GetIdx()+1],
                             forces[atom.GetIdx()+2]))


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <molfile>" % argv[0])

    epsin = 1.0
    zap = oezap.OEZap()
    zap.SetInnerDielectric(epsin)

    mol = oechem.OEGraphMol()
    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    while oechem.OEReadMolecule(ifs, mol):
        PrintHeader(mol.GetTitle())
        forces = oechem.OEFloatArray(mol.GetMaxAtomIdx()*3)
        oechem.OEAssignBondiVdWRadii(mol)
        oechem.OEMMFFAtomTypes(mol)
        oechem.OEMMFF94PartialCharges(mol)
        zap.SetMolecule(mol)
        zap.CalcForces(forces)
        PrintForces(mol, forces)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
