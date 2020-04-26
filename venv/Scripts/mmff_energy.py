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
# The following function is an example to show how to evaluate energies   //
# of a small molecule and obtain various energy components.               //
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

        vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
        mol.GetCoords(vecCoords)
        for fcomp in mmff.GetFComponents(vecCoords):
            oechem.OEThrow.Info("Molecule: %s Component: %s Energy: %d kcal/mol"
                                % (mol.GetTitle(), fcomp.name, fcomp.value))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
