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


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("calc_et.py <reffile> <fitfile>")

    refmol = oechem.OEGraphMol()

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    oechem.OEReadMolecule(ifs, refmol)
    oechem.OEAssignBondiVdWRadii(refmol)
    oechem.OEMMFFAtomTypes(refmol)
    oechem.OEMMFF94PartialCharges(refmol)

    et = oezap.OEET()
    et.SetRefMol(refmol)

    oechem.OEThrow.Info("dielectric: %.4f" % et.GetDielectric())
    oechem.OEThrow.Info("inner mask: %.4f" % et.GetInnerMask())
    oechem.OEThrow.Info("outer mask: %.4f" % et.GetOuterMask())
    oechem.OEThrow.Info("salt conc : %.4f" % et.GetSaltConcentration())
    oechem.OEThrow.Info("join      : %d" % et.GetJoin())

    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])

    fitmol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, fitmol):
        oechem.OEAssignBondiVdWRadii(fitmol)
        oechem.OEMMFFAtomTypes(fitmol)
        oechem.OEMMFF94PartialCharges(fitmol)
        oechem.OEThrow.Info("Title: %s, ET %4.2f" %
                            (fitmol.GetTitle(), et.Tanimoto(fitmol)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
