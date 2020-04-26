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
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <input> <output>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[2])

    mol = oechem.OEMol()
    oechem.OEReadMolecule(ifs, mol)

    opts = oeszybki.OEFreeFormConfOptions()
    ffconf = oeszybki.OEFreeFormConf(opts)

    omol = oechem.OEMol(mol)
    if not (ffconf.EstimateFreeEnergies(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Failed to estimate conformational free energies")

    res = oeszybki.OEFreeFormConfResults(omol)
    oechem.OEThrow.Info("Number of unique conformations: %d" % res.GetNumUniqueConfs())
    oechem.OEThrow.Info("Conf.  Delta_G   Vibrational_Entropy")
    oechem.OEThrow.Info("      [kcal/mol]     [J/(mol K)]")
    for r in res.GetResultsForConformations():
        oechem.OEThrow.Info("%2d %10.2f %14.2f" % (r.GetConfIdx(), r.GetDeltaG(),
                                                   r.GetVibrationalEntropy()))

    oechem.OEWriteMolecule(ofs, omol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
