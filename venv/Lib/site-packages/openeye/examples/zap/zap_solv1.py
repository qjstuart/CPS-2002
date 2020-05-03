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
from openeye import oezap

KCalsPerKT = 0.59
KCalsPerSqAngstrom = 0.025


def PrintHeader():
    print("Title        Solv(kcal)   Area(Ang^2)   Total(kcal)  Int.Coul(kcal)\n")


def PrintLine(title, solv, area, coul):
    total = KCalsPerKT*solv + KCalsPerSqAngstrom*area
    print("%-12s   %6.2f       %6.2f       %6.2f          %6.2f" %
          (title, KCalsPerKT*solv, area, total, KCalsPerKT*coul))


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <molfile>" % argv[0])

    epsin = 1.0

    zap = oezap.OEZap()
    zap.SetInnerDielectric(epsin)
    zap.SetGridSpacing(0.5)

    area = oezap.OEArea()

    PrintHeader()
    mol = oechem.OEGraphMol()
    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    while oechem.OEReadMolecule(ifs, mol):
        oechem.OEAssignBondiVdWRadii(mol)
        oechem.OEMMFFAtomTypes(mol)
        oechem.OEMMFF94PartialCharges(mol)
        zap.SetMolecule(mol)
        solv = zap.CalcSolvationEnergy()
        aval = area.GetArea(mol)
        coul = oezap.OECoulombicSelfEnergy(mol, epsin)
        PrintLine(mol.GetTitle(), solv, aval, coul)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
