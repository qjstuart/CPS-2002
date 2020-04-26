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
from openeye import oegrid
from openeye import oespicoli


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <ref> <fit>" % args[0])

    refifs = oechem.oemolistream()
    if not refifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    refmol = oechem.OEGraphMol()
    oechem.OEReadMolecule(refifs, refmol)
    oechem.OEAssignBondiVdWRadii(refmol)

    fitifs = oechem.oemolistream()
    if not fitifs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[2])

    fitmol = oechem.OEGraphMol()
    oechem.OEReadMolecule(fitifs, fitmol)
    oechem.OEAssignBondiVdWRadii(fitmol)

    # Map the reference molecule onto a grid
    grd = oegrid.OEScalarGrid()
    oegrid.OEMakeMolecularGaussianGrid(grd, refmol, 0.5)

    # Get the total volume of the reference molecule
    refsrf = oespicoli.OESurface()
    oespicoli.OEMakeSurfaceFromGrid(refsrf, grd, 1.0)
    totalv = oespicoli.OESurfaceVolume(refsrf)

    # Mask out the fit molecule
    oegrid.OEMaskGridByMolecule(grd, fitmol)

    # Find how much of the reference volume is remaining
    fitsrf = oespicoli.OESurface()
    oespicoli.OEMakeSurfaceFromGrid(fitsrf, grd, 1.0)
    remaining = oespicoli.OESurfaceVolume(fitsrf)

    print("Percent overlap: %f" % ((1 - remaining/totalv) * 100))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
