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
# The following example demonstrates how to perform ligand optimization   //
# in the context of a protein using MMFFAmber force field.                //
# //////////////////////////////////////////////////////////////////////////


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <input> <output>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading " % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[3])

    # Load the protein molecule and Prepare with MMFF
    smir = oeff.OESmirnoff()
    optimizer = oeff.OENewtonOpt()

    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, mol):
        if ((not smir.PrepMol(mol)) or (not smir.Setup(mol))):
            oechem.OEThrow.Warning("Unable to process molecule: title = '%s'" % mol.GetTitle())
            oechem.OEWriteMolecule(ofs, mol)
            continue

        vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
        for conf in mol.GetConfs():
            oechem.OEThrow.Info("Molecule: %s Conformer: %d" % (mol.GetTitle(), conf.GetIdx()+1))
            conf.GetCoords(vecCoords)

            energy = smir(vecCoords)
            oechem.OEThrow.Info("Initial energy: %d kcal/mol" % energy)

            energy = optimizer(smir, vecCoords, vecCoords)
            oechem.OEThrow.Info("Optimized energy: %d kcal/mol" % energy)
            conf.SetCoords(vecCoords)

        oechem.OEWriteMolecule(ofs, mol)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
