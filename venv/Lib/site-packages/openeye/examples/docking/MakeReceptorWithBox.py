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
from openeye import oedocking


def main(argv=[__name__]):
    if len(sys.argv) != 8:
        oechem.OEThrow.Usage("MakeReceptorFromBox.py \
                              <protein> <xmax> <ymax> <zmax> <xmin> <ymin> <zmin>")

    xmax = float(sys.argv[2])
    ymax = float(sys.argv[3])
    zmax = float(sys.argv[4])
    xmin = float(sys.argv[5])
    ymin = float(sys.argv[6])
    zmin = float(sys.argv[7])

    # @ <SNIPPET-MAKE-RECEPTOR-WITH-BOX-1>
    imstr = oechem.oemolistream(sys.argv[1])
    proteinStructure = oechem.OEGraphMol()
    oechem.OEReadMolecule(imstr, proteinStructure)

    box = oedocking.OEBox(xmax, ymax, zmax, xmin, ymin, zmin)
    receptor = oechem.OEGraphMol()
    oedocking.OEMakeReceptor(receptor, proteinStructure, box)
    # @ </SNIPPET-MAKE-RECEPTOR-WITH-BOX-1>

    oedocking.OEWriteReceptorFile(receptor, "receptor.oeb.gz")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
