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
# in the context of a protein using MMFF force field.                     //
# //////////////////////////////////////////////////////////////////////////


def GetBoundsFromMol(bounds, mol, pad):
    set = False
    c = oechem.OEDoubleArray(3)
    for atom in mol.GetAtoms():
        mol.GetCoords(atom, c)
        if not set:
            bounds[0] = bounds[3] = c[0]
            bounds[1] = bounds[4] = c[1]
            bounds[2] = bounds[5] = c[2]
            set = True
        else:
            if (c[0] < bounds[0]):
                bounds[0] = c[0]
            if (c[1] < bounds[1]):
                bounds[1] = c[1]
            if (c[2] < bounds[2]):
                bounds[2] = c[2]
            if (c[0] > bounds[3]):
                bounds[3] = c[0]
            if (c[1] > bounds[4]):
                bounds[4] = c[1]
            if (c[2] > bounds[5]):
                bounds[5] = c[2]

    bounds[0] -= pad
    bounds[1] -= pad
    bounds[2] -= pad
    bounds[3] += pad
    bounds[4] += pad
    bounds[5] += pad


def main(args):
    if len(args) != 5:
        oechem.OEThrow.Usage("%s <protein> <ligand> <bound-ligand> <output>" % args[0])

    ips = oechem.oemolistream()
    if not ips.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading protein" % args[1])

    ils = oechem.oemolistream()
    if not ils.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading ligand" % args[2])

    ibs = oechem.oemolistream()
    if not ibs.open(args[3]):
        oechem.OEThrow.Fatal("Unable to open %s for reading bound ligand" % args[3])

    ofs = oechem.oemolostream()
    if not ofs.open(args[4]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[4])

    # Load the protein molecule and Prepare with MMFF
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(ips, protein)
    oechem.OEAddExplicitHydrogens(protein)
    mmff2 = oeff.OEMMFF()
    mmff = oeff.OEGenericFF(mmff2)
    mmff.PrepMol(protein)

    # Get bounds for protein ligand interaction
    bounds = oechem.OEDoubleArray(6)
    boundsMol = oechem.OEGraphMol()
    oechem.OEReadMolecule(ibs, boundsMol)
    GetBoundsFromMol(bounds, boundsMol, 5.0)

    # Create intermolecular interaction functions and add to MMFF
    params = oeff.OEMMFFParams()
    interVdw = oeff.OEMMFFInterVdwNN(protein, params, bounds)
    interCoul = oeff.OEMMFFInterCoulomb(protein, bounds, 1.0, 1.0, 0.5)
    mmff.Add(interVdw)
    mmff.Add(interCoul)

    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ils, mol):
        oechem.OEAddExplicitHydrogens(mol)

        if (not mmff.PrepMol(mol)) or (not mmff.Setup(mol)):
            oechem.OEThrow.Warning("Unable to process molecule: title = '%s'" % mol.GetTitle())
            oechem.OEWriteMolecule(ofs, mol)
            continue

        vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
        for conf in mol.GetConfs():
            oechem.OEThrow.Info("Molecule: %s Conformer: %d" % (mol.GetTitle(), conf.GetIdx()+1))
            conf.GetCoords(vecCoords)

            # Calculate energy
            energy = mmff(vecCoords)
            oechem.OEThrow.Info("Initial energy: %d kcal/mol" % energy)

            # Optimize the ligand
            optimizer = oeff.OEBFGSOpt()
            energy = optimizer(mmff, vecCoords, vecCoords)
            oechem.OEThrow.Info("Optimized energy: %d kcal/mol" % energy)
            conf.SetCoords(vecCoords)

        oechem.OEWriteMolecule(ofs, mol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
