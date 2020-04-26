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
    if len(argv) != 3:
        oechem.OEThrow.Usage("SetOuterContourVolume.py <receptor> <volume>")

    receptor = oechem.OEGraphMol()
    if not oedocking.OEReadReceptorFile(receptor, argv[1]):
        oechem.OEThrow.Fatal("Unable to open receptor file")

    outerContourVolume = float(argv[2])

    # @ <SNIPPET-SET-OUTER-CONTOUR-VOLUME-1>
    negativeImagePotential = oedocking.OEReceptorGetNegativeImageGrid(receptor)

    gridElement = []
    for i in range(negativeImagePotential.GetSize()):
        gridElement.append(negativeImagePotential[i])

    gridElement.sort()
    gridElement.reverse()

    countToVolume = pow(negativeImagePotential.GetSpacing(), 3)
    ilevel = int((outerContourVolume / countToVolume) + 0.5)

    outerContourLevel = gridElement[-1]
    if ilevel < len(gridElement):
        outerContourLevel = gridElement[ilevel]

    oedocking.OEReceptorSetOuterContourLevel(receptor, outerContourLevel)
    # @ </SNIPPET-SET-OUTER-CONTOUR-VOLUME-1>

    if not oedocking.OEWriteReceptorFile(receptor, argv[1]):
        oechem.OEThrow.Fatal("Unable to write updated receptor")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
