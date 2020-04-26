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
from openeye import oespicoli


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <protein> <surface>" % args[0])

    prtfs = oechem.oemolistream()
    if not prtfs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    prt = oechem.OEGraphMol()
    oechem.OEReadMolecule(prtfs, prt)
    oechem.OEAssignBondiVdWRadii(prt)

    surf = oespicoli.OESurface()
    oespicoli.OEMakeCavitySurfaces(prt, surf)

    oespicoli.OEInvertSurface(surf)

    oespicoli.OEWriteSurface(args[2], surf)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
