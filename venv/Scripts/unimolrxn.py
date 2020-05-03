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
# Perform reactions on the given compounds
#############################################################################
import sys
from openeye import oechem


def UniMolRxn(ifs, ofs, umr):
    for mol in ifs.GetOEGraphMols():
        if umr(mol):
            oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    if not (3 <= len(argv) <= 4):
        oechem.OEThrow.Usage("%s SMIRKS <infile> [<outfile>]" % argv[0])

    qmol = oechem.OEQMol()
    if not oechem.OEParseSmirks(qmol, argv[1]):
        oechem.OEThrow.Fatal("Unable to parse SMIRKS: %s" % argv[1])

    umr = oechem.OEUniMolecularRxn()
    if not umr.Init(qmol):
        oechem.OEThrow.Fatal("Failed to initialize reaction with %s SMIRKS" % argv[1])
    umr.SetClearCoordinates(True)

    ifs = oechem.oemolistream()
    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])

    ofs = oechem.oemolostream(".ism")
    if len(argv) == 4:
        if not ofs.open(argv[3]):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[3])

    UniMolRxn(ifs, ofs, umr)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
