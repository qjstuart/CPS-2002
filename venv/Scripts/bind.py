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
from openeye import oezap


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <protein> <ligands>" % argv[0])

    protein = oechem.OEMol()

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    oechem.OEReadMolecule(ifs, protein)

    oechem.OEAssignBondiVdWRadii(protein)
    oechem.OEMMFFAtomTypes(protein)
    oechem.OEMMFF94PartialCharges(protein)
    print("protein:   " + protein.GetTitle())

    epsin = 1.0
    bind = oezap.OEBind()
    bind.GetZap().SetInnerDielectric(epsin)
    bind.SetProtein(protein)
    results = oezap.OEBindResults()

    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    ifs.SetConfTest(oechem.OEIsomericConfTest())

    ligand = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, ligand):
        oechem.OEAssignBondiVdWRadii(ligand)
        oechem.OEMMFFAtomTypes(ligand)
        oechem.OEMMFF94PartialCharges(ligand)
        print("ligand:  %s has %d conformers" %
              (ligand.GetTitle(), ligand.NumConfs()))

        for conf in ligand.GetConfs():
            bind.Bind(conf, results)
            print(" conf# %d   be = %f" %
                  (conf.GetIdx(), results.GetBindingEnergy()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
