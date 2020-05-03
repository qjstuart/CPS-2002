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

#############################################################################
# Output some basic molecule properties
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <infile>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])

    print("Title MolWt NumAtoms NumHeavyAtoms NumRingAtoms NumRotors NumConfs")

    for mol in ifs.GetOEMols():
        title = mol.GetTitle()
        if not title:
            title = "Untitled"
        print("%s %.3f %d %d %d %d %d" % (title,
                                          oechem.OECalculateMolecularWeight(mol),
                                          mol.NumAtoms(),
                                          oechem.OECount(mol, oechem.OEIsHeavy()),
                                          oechem.OECount(mol, oechem.OEAtomIsInRing()),
                                          oechem.OECount(mol, oechem.OEIsRotor()),
                                          mol.NumConfs()))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
