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
# The following function is an example to show how to evaluate energy     //
# and optimize a set of torsions in a small molecule                      //
# using the MMFF force field.                                             //
# //////////////////////////////////////////////////////////////////////////


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <input> <output>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[2])

    mmff = oeff.OEMMFF()

    # Setup adaptor. The first (false) means not to pass ownership of mmff,
    # and the second (false) means not to exclude interactions related
    # to the subset which would be fixed for calculations.
    adaptor = oeff.OETorAdaptor(mmff, False, False)

    # Use a simple predicate for the subset of torsions to optimize
    adaptor.Set(oechem.OEIsRotor())

    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, mol):
        oechem.OEAddExplicitHydrogens(mol)

        # Use a simple atoms predicate for the subset, followed by setup
        if (not mmff.PrepMol(mol)) or (not adaptor.Setup(mol)):
            oechem.OEThrow.Warning("Unable to process molecule: title = '%s'" % mol.GetTitle())
            oechem.OEWriteMolecule(ofs, mol)
            continue

        vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
        for conf in mol.GetConfs():
            oechem.OEThrow.Info("Molecule: %s Conformer: %d" % (mol.GetTitle(), conf.GetIdx()+1))
            conf.GetCoords(vecCoords)

            # Get adaptor variables set corresponding to the coordinates
            vecX = oechem.OEDoubleArray(adaptor.NumVar())
            adaptor.GetVar(vecX, vecCoords)

            # Calculate energy using adaptor
            energy = adaptor(vecX)
            oechem.OEThrow.Info("Initial energy: %d kcal/mol" % energy)

            # Optimize the adaptor
            optimizer = oeff.OEBFGSOpt()
            energy = optimizer(adaptor, vecX, vecX)
            oechem.OEThrow.Info("Optimized energy: %d kcal/mol" % energy)

            # Get optimized coordinates corresponding to the adaptor optimized variables
            adaptor.AdaptVar(vecCoords, vecX)
            conf.SetCoords(vecCoords)

        oechem.OEWriteMolecule(ofs, mol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
