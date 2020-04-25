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
from openeye import oedocking


def main(argv=[__name__]):
    if len(sys.argv) != 2:
        oechem.OEThrow.Usage("ReceptorOuterContourVolume.py <receptor>")

    receptor = oechem.OEGraphMol()

    if not oedocking.OEReadReceptorFile(receptor, sys.argv[1]):
        oechem.OEThrow.Fatal("%s is not a valid receptor", argv[1])

    # @ <SNIPPET-RECEPTOR-OUTER-CONTOUR-VOLUME-1>
    negativeImagePotential = oedocking.OEReceptorGetNegativeImageGrid(receptor)
    outerContourLevel = oedocking.OEReceptorGetOuterContourLevel(receptor)

    outerCount = 0
    for i in range(negativeImagePotential.GetSize()):
        if negativeImagePotential[i] >= outerContourLevel:
            outerCount += 1

    countToVolume = pow(negativeImagePotential.GetSpacing(), 3)

    print(outerCount * countToVolume, " cubic angstroms")
    # @ </SNIPPET-RECEPTOR-OUTER-CONTOUR-VOLUME-1>


if __name__ == "__main__":
    sys.exit(main(sys.argv))
