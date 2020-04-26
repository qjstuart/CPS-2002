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
from openeye import oechem
from openeye import oequacpac


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <infile>" % argv[0])

    ifs = oechem.oemolistream(sys.argv[1])
    am1 = oequacpac.OEAM1()
    results = oequacpac.OEAM1Results()
    for mol in ifs.GetOEMols():
        for conf in mol.GetConfs():
            print("molecule: ", mol.GetTitle(), "conformer:", conf.GetIdx())
            if am1.CalcAM1(results, mol):
                nbonds = 0
                for bond in mol.GetBonds(oechem.OEIsRotor()):
                    nbonds += 1
                    print(results.GetBondOrder(bond.GetBgnIdx(), bond.GetEndIdx()))
                print("Rotatable bonds: ", nbonds)


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
