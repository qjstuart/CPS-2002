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
import os
import sys

from openeye import oechem
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))


def main(argv=[__name__]):
    if len(argv) < 3:
        oechem.OEThrow.Usage("%s input.oeb output_prepped_database.oeb" % argv[0])
        return 0

    # Input mol stream
    ifs = oechem.oemolistream()
    ifs.open(argv[1])

    # PRE-Compress output mol stream
    ofs = oechem.oemolostream()
    oechem.OEPRECompress(ofs)
    ofs.open(argv[2])

    # Prepare mol & write to stream
    for mol in ifs.GetOEMols():
        oefastrocs.OEPrepareFastROCSMol(mol)
        halfMol = oechem.OEMol(mol, oechem.OEMCMolType_HalfFloatCartesian)
        oechem.OEWriteMolecule(ofs, halfMol)

    ofs.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
