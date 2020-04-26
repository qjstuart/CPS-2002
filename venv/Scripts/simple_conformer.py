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
from openeye import oequacpac
from openeye import oeszybki


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s input_molecule output_molecule" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[2])

    opts = oeszybki.OESzybkiOptions()
    opts.GetOptOptions().SetOptimizerType(oeszybki.OEOptType_NEWTON)
    opts.GetGeneralOptions().SetForceFieldType(oeszybki.OEForceFieldType_MMFF94S)
    opts.GetSolventOptions().SetSolventModel(oeszybki.OESolventModel_Sheffield)
    opts.GetSolventOptions().SetChargeEngine(oequacpac.OEChargeEngineNoOp())
    sz = oeszybki.OESzybki(opts)
    res = oeszybki.OESzybkiResults()
    for mol in ifs.GetOEMols():
        for conf in mol.GetConfs():
            if sz(conf, res):
                oechem.OESetSDData(conf, oechem.OESDDataPair('Total_energy', "%0.4f"
                                                             % res.GetTotalEnergy()))

        oechem.OEWriteMolecule(ofs, mol)

    ifs.close()
    ofs.close()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
