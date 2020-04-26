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
from openeye import oeff

# //////////////////////////////////////////////////////////////////////////
# The following example demonstrates how to obtain interactions           //
# of a small molecule in the context of MMFF force field.                 //
# //////////////////////////////////////////////////////////////////////////


def main(args):
    if len(args) != 2:
        oechem.OEThrow.Usage("%s <input>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        oechem.OEAddExplicitHydrogens(mol)

        mmff = oeff.OEMMFF()
        if not mmff.PrepMol(mol) or not mmff.Setup(mol):
            oechem.OEThrow.Warning("Unable to process molecule: title = '%s'" % mol.GetTitle())
            continue

        # print out interactions
        vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
        mol.GetCoords(vecCoords)
        oechem.OEThrow.Info("Molecule: %s" % mol.GetTitle())
        for intc in mmff.GetInteractions(mol, vecCoords):
            vecGrads = oechem.OEDoubleArray(intc.NumValues())
            oechem.OEThrow.Info("Interaction: %s Value: %d"
                                % (intc.GetName(), intc.GetValues(vecGrads)))

            for atom in intc.GetAtoms():
                oechem.OEThrow.Info("Atom index: %d" % atom.GetIdx())

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
