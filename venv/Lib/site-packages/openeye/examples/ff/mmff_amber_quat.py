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
# The following example demonstrates how to perform rigid optimization of //
# a ligand in the context of a protein using MMFFAmber force field. The   //
# OEQuatAdaptor it used for rigid optimization.                           //
# //////////////////////////////////////////////////////////////////////////


def main(args):
    if len(args) != 4:
        oechem.OEThrow.Usage("%s <protein> <ligand> <output>" % args[0])

    ips = oechem.oemolistream()
    if not ips.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading protein" % args[1])

    ils = oechem.oemolistream()
    if not ils.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading ligand" % args[2])

    ofs = oechem.oemolostream()
    if not ofs.open(args[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[3])

    # Load the protein molecule and Prepare with MMFF
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(ips, protein)
    oechem.OEAddExplicitHydrogens(protein)
    mmff = oeff.OEMMFFAmber(protein)
    mmff.PrepMol(protein)

    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ils, mol):
        oechem.OEAddExplicitHydrogens(mol)
        if (not mmff.PrepMol(mol)) or (not mmff.Setup(mol)):
            oechem.OEThrow.Warning("Unable to process molecule: title = '%s'" % mol.GetTitle())
            oechem.OEWriteMolecule(ofs, mol)
            continue

        # Setup adaptor. The first (false) means not to pass ownership of mmff,
        # and the second (false) means not to exclude interactions related
        # to the subset which would be fixed for calculations.
        adaptor = oeff.OEQuatAdaptor(mmff, False, False)
        if not adaptor.Setup(mol):
            oechem.OEThrow.Warning("Unable to process subset for molecule: title = '%s'"
                                   % mol.GetTitle())
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

            # Optimize the ligand
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
