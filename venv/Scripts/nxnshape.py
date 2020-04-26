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

from openeye import oechem
from openeye import oeshape


def oneConf(conf, prep, filename, csvfile):
    csvfile.write("%s_%d" % (conf.GetTitle(), conf.GetIdx()))
    refmol = oechem.OEGraphMol(conf)

    options = oeshape.OEOverlayOptions()
    options.SetOverlapFunc(oeshape.OEGridShapeFunc())
    overlay = oeshape.OEOverlay(options)
    overlay.SetupRef(refmol)

    bfs = oechem.oemolistream(filename)
    fitmol = oechem.OEMol()
    while oechem.OEReadMolecule(bfs, fitmol):
        prep.Prep(fitmol)
        scoreiter = oeshape.OEBestOverlayScoreIter()
        oeshape.OESortOverlayScores(scoreiter, overlay.Overlay(fitmol), oeshape.OEHighestTanimoto(), 1, True)

        for score in scoreiter:
            csvfile.write(",%.2f" % score.GetTanimoto())
    csvfile.write("\n")


def genHeader(filename, csvfile):
    csvfile.write("name")
    ifs = oechem.oemolistream(filename)
    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, mol):
        for conf in mol.GetConfs():
            csvfile.write(",%s_%d" % (conf.GetTitle(), conf.GetIdx()))
    csvfile.write("\n")


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <infile> <csvfile>" % argv[0])

    csvfile = open(argv[2], "w")
    genHeader(sys.argv[1], csvfile)

    prep = oeshape.OEOverlapPrep()
    prep.SetAssignColor(False)
    afs = oechem.oemolistream(argv[1])
    for molA in afs.GetOEMols():
        prep.Prep(molA)
        print(molA.GetTitle())
        for conf in molA.GetConfs():
            oneConf(conf, prep, sys.argv[1], csvfile)


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
