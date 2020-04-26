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
from openeye import oeszybki


def main(args):
    if len(args) != 2:
        oechem.OEThrow.Usage("%s <lig>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    lig = oechem.OEMol()
    oechem.OEReadMolecule(ifs, lig)

    szOpts = oeszybki.OESzybkiOptions()
    szOpts.GetSolventOptions().SetSolventModel(oeszybki.OESolventModel_Sheffield)
    sz = oeszybki.OESzybki(szOpts)
    eres = oeszybki.OESzybkiEnsembleResults()
    S = sz.GetEntropy(lig, eres, oeszybki.OEEntropyMethod_Analytic)

    print("Configurational entropy %10.2f" % eres.GetConfigurationalEntropy())
    print("Solvation entropy       %10.2f" % eres.GetEnsembleLigSolvEntropy())
    print("                            ======")
    print("Total solution entropy  %10.2f J/(mol K)" % S)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
