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
from openeye import oeszybki


def main(args):
    if len(args) != 4:
        oechem.OEThrow.Usage("%s bound_ligand protein opt_ligand" % args[0])

    lfs = oechem.oemolistream()
    if not lfs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    pfs = oechem.oemolistream()
    if not pfs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[2])

    ofs = oechem.oemolostream()
    if not ofs.open(args[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[3])

    lig = oechem.OEMol()
    oechem.OEReadMolecule(lfs, lig)

    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(pfs, protein)

    szOpts = oeszybki.OESzybkiOptions()
    sz = oeszybki.OESzybki(szOpts)
    sz.SetProtein(protein)

    eres = oeszybki.OESzybkiEnsembleResults()
    entropy = sz.GetEntropy(lig, eres, oeszybki.OEEntropyMethod_Analytic,
                            oeszybki.OEEnvType_Protein)

    oechem.OEThrow.Info("Estimated entropy of the bound ligand is: %5.1f J/(mol*K)" % entropy)

    oechem.OEWriteMolecule(ofs, lig)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
