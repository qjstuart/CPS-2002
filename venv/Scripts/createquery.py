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

from openeye import oechem
from openeye import oegrid
from openeye import oeshape


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <molfile> <queryfile>" % sys.argv[0])

    molfs = oechem.oemolistream(sys.argv[1])
    mol = oechem.OEGraphMol()
    oechem.OEReadMolecule(molfs, mol)

    if oechem.OEGetFileExtension(sys.argv[2]) != "sq":
        oechem.OEThrow.Fatal("Only can write shape query to .sq output file format")

    # Use OEOverlapPrep to remove hydrogens and add
    # color atoms to the molecule
    prep = oeshape.OEOverlapPrep()
    prep.Prep(mol)

    # Get the color atoms, create gaussians and add them
    # to the shape query
    query = oeshape.OEShapeQuery()
    for atom in oeshape.OEGetColorAtoms(mol):
        coords = oechem.OEFloatArray(3)
        mol.GetCoords(atom, coords)
        gauss = oegrid.OEGaussian(1.0, 1.0, coords, oeshape.OEGetColorType(atom))
        query.AddColorGaussian(gauss)

    # Remove color atoms from the molecule and add to the query
    oeshape.OERemoveColorAtoms(mol)
    query.SetMolecule(mol)

    oeshape.OEWriteShapeQuery(sys.argv[2], query)
    print("shape query created")


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
