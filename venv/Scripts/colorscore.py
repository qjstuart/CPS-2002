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


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <reffile> <rocs_hits_file> <output.sdf>" % argv[0])

    reffs = oechem.oemolistream(argv[1])
    fitfs = oechem.oemolistream(argv[2])
    outfs = oechem.oemolostream(argv[3])

    refmol = oechem.OEGraphMol()
    oechem.OEReadMolecule(reffs, refmol)

    # Prepare reference molecule for calculation
    # With default options this will add required color atoms
    prep = oeshape.OEOverlapPrep()
    prep.Prep(refmol)

    # Get appropriate function to calculate analytic color
    colorFunc = oeshape.OEAnalyticColorFunc()
    colorFunc.SetupRef(refmol)

    res = oeshape.OEOverlapResults()
    for fitmol in fitfs.GetOEGraphMols():
        prep.Prep(fitmol)
        colorFunc.Overlap(fitmol, res)
        oechem.OESetSDData(fitmol, "AnalyticColorTanimoto", "%.2f" % res.GetColorTanimoto())
        oechem.OEWriteMolecule(outfs, fitmol)
        print("Fit Title: %s  Color Tanimoto: %.2f" %
              (fitmol.GetTitle(), res.GetColorTanimoto()))


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
