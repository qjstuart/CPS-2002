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

# This example reads in a reference molecule and a few fit
# molecules, performs overlay optimization, sorts the results
# in Tanimoto order, and shows the single best result.
# With the default options, OEOverlay optimizes both shape and color.

from __future__ import print_function

import sys

from openeye import oechem
from openeye import oeshape


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <reffile> <fitfile>" % argv[0])

    reffs = oechem.oemolistream(argv[1])
    fitfs = oechem.oemolistream(argv[2])

    refmol = oechem.OEMol()
    oechem.OEReadMolecule(reffs, refmol)
    print("Ref. Title:", refmol.GetTitle(), "Num Confs:", refmol.NumConfs())

    # Prepare reference molecule for calculation
    # With default options this will remove any explicit
    # hydrogens present and add color atoms
    prep = oeshape.OEOverlapPrep()
    prep.Prep(refmol)

    overlay = oeshape.OEMultiRefOverlay()
    overlay.SetupRef(refmol)

    for fitmol in fitfs.GetOEMols():
        prep.Prep(fitmol)
        score = oeshape.OEBestOverlayScore()
        overlay.BestOverlay(score, fitmol, oeshape.OEHighestTanimoto())
        print("Fit Title: %-4s FitConfIdx: %-4d RefConfIdx: %-4d tanimoto combo: %.2f"
              % (fitmol.GetTitle(), score.GetFitConfIdx(),
                 score.GetRefConfIdx(), score.GetTanimotoCombo()))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
