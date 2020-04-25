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
# in tanimoto order, shows the user specified number of
# results, and saves the overlayed structures.
# With the default options, OEOverlay optimizes both shape and color.

from __future__ import print_function

from openeye import oechem
from openeye import oeshape


def main(argv=[__name__]):
    if len(argv) != 5:
        oechem.OEThrow.Usage("%s <reffile> <fitfile> <out.sdf> <keepsize>" % argv[0])

    reffs = oechem.oemolistream(argv[1])
    fitfs = oechem.oemolistream(argv[2])
    outfs = oechem.oemolostream(argv[3])
    keepsize = int(argv[4])

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
        print("Fit Title:", fitmol.GetTitle(), "Num Confs:", fitmol.NumConfs())

        prep.Prep(fitmol)
        resCount = 0

        # Sort all scores according to highest tanimoto
        scoreiter = oeshape.OEBestOverlayScoreIter()
        oeshape.OESortOverlayScores(scoreiter, overlay.Overlay(fitmol), oeshape.OEHighestTanimoto())

        for score in scoreiter:
            outmol = oechem.OEGraphMol(fitmol.GetConf(oechem.OEHasConfIdx(score.GetFitConfIdx())))
            score.Transform(outmol)

            oechem.OESetSDData(outmol, "RefConfIdx", "%-d" % score.GetRefConfIdx())
            oechem.OESetSDData(outmol, "tanimoto combo", "%-.3f" % score.GetTanimotoCombo())

            oechem.OEWriteMolecule(outfs,
                                   refmol.GetConf(oechem.OEHasConfIdx(score.GetRefConfIdx())))
            oechem.OEWriteMolecule(outfs, outmol)

            resCount += 1

            # Break at the user specified size
            if resCount == keepsize:
                break

        print(resCount, "results returned")


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
