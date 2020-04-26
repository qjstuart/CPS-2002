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
    if len(argv) != 5:
        oechem.OEThrow.Usage("%s <reffile> <fitfile> <outfile> <nhits>" % argv[0])

    reffs = oechem.oemolistream(sys.argv[1])
    fitfs = oechem.oemolistream(sys.argv[2])
    outfs = oechem.oemolostream(sys.argv[3])
    nhits = int(sys.argv[4])

    refmol = oechem.OEMol()
    oechem.OEReadMolecule(reffs, refmol)

    # Setup OEROCS with specified number of best hits
    options = oeshape.OEROCSOptions()
    options.SetNumBestHits(nhits)
    rocs = oeshape.OEROCS(options)
    rocs.SetDatabase(fitfs)
    for res in rocs.Overlay(refmol):
        outmol = res.GetOverlayConf()
        oechem.OEWriteMolecule(outfs, outmol)
        print("title: %s  tanimoto combo = %.2f" % (outmol.GetTitle(), res.GetTanimotoCombo()))


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
