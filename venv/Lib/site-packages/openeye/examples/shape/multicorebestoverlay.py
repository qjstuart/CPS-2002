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

# This is a multi-threaded version of the example that reads in a
# reference molecule and a few fit molecules, performs overlay optimization,
# and shows the single best result.
# With the default options, OEOverlay optimizes both shape and color.

from __future__ import print_function
import sys
from openeye import oechem
from openeye import oeshape
from threading import Thread


class MultiCoreOverlay(Thread):
    def __init__(self, refmol, ifs):
        Thread.__init__(self)
        self._prep = oeshape.OEOverlapPrep()
        self._prep.Prep(refmol)
        self._overlay = oeshape.OEMultiRefOverlay()
        self._overlay.SetupRef(refmol)
        self._ifs = ifs

    def run(self):
        for fitmol in self._ifs.GetOEMols():
            self._prep.Prep(fitmol)
            score = oeshape.OEBestOverlayScore()
            self._overlay.BestOverlay(score, fitmol, oeshape.OEHighestTanimoto())
            print("Fit Title: %-4s FitConfIdx: %-4d RefConfIdx: %-4d tanimoto combo: %.2f"
                  % (fitmol.GetTitle(), score.GetFitConfIdx(),
                     score.GetRefConfIdx(), score.GetTanimotoCombo()))


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <reffile> <fitfile>" % argv[0])

    reffs = oechem.oemolistream(argv[1])
    refmol = oechem.OEMol()
    oechem.OEReadMolecule(reffs, refmol)
    print("Ref. Title:", refmol.GetTitle(), "Num Confs:", refmol.NumConfs())

    fitfs = oechem.oemolithread(sys.argv[2])

    thrds = []
    for i in range(oechem.OEGetNumProcessors()):
        thrd = MultiCoreOverlay(refmol, fitfs)
        thrd.start()
        thrds.append(thrd)

    for thrd in thrds:
        thrd.join()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
