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

# ///////////////////////////////////////////////////////////////////////////
# The following function is a contrived example to show how to             //
# write a user-defined function.  The energy function is the square        //
# of the distance from the origin.  The derivative then is two times the   //
# coordinate component.  The function will attempt to place all atoms of   //
# a molecule at the origin.                                                //
# ///////////////////////////////////////////////////////////////////////////


class Harmonic(oeff.OEMolFunc1):
    def __init__(self):
        oeff.OEMolFunc1.__init__(self)
        self.natoms = 0
        pass

    def begin(self):
        pass

    def NumVar(self):
        return 3*self.natoms

    def Setup(self, mol):
        self.natoms = mol.GetMaxAtomIdx()
        return True

    def __call__(self, coord, grad=None):
        energy = 0.0
        if isinstance(coord, oechem.OEDoubleArray):
            if grad is not None:
                for i in range(0, self.natoms):
                    grad[3*i] += 2.0 * coord[3*i]  # x gradient
                    grad[3*i+1] += 2.0 * coord[3*i+1]  # y gradient
                    grad[3*i+2] += 2.0 * coord[3*i+2]  # z gradient
                    energy += coord[3*i] * coord[3*i]  # x distance from zero
                    energy += coord[3*i+1] * coord[3*i+1]  # y distance from zero
                    energy += coord[3*i+2] * coord[3*i+2]  # z distance from zero
            else:
                for i in range(0, self.natoms):
                    energy += coord[3*i] * coord[3*i]  # x distance from zero
                    energy += coord[3*i+1] * coord[3*i+1]  # y distance from zero
                    energy += coord[3*i+2] * coord[3*i+2]  # z distance from zero
        else:
            coord1 = oechem.OEDoubleArray(coord, self.NumVar(), False)
            if grad is not None:
                grad1 = oechem.OEDoubleArray(grad, self.NumVar(), False)
                for i in range(0, self.natoms):
                    grad1[3*i] += 2.0 * coord1[3*i]  # x gradient
                    grad1[3*i+1] += 2.0 * coord1[3*i+1]  # y gradient
                    grad1[3*i+2] += 2.0 * coord1[3*i+2]  # z gradient
                    energy += coord1[3*i] * coord1[3*i]  # x distance from zero
                    energy += coord1[3*i+1] * coord1[3*i+1]  # y distance from zero
                    energy += coord1[3*i+2] * coord1[3*i+2]  # z distance from zero
            else:
                for i in range(0, self.natoms):
                    energy += coord1[3*i] * coord1[3*i]  # x distance from zero
                    energy += coord1[3*i+1] * coord1[3*i+1]  # y distance from zero
                    energy += coord1[3*i+2] * coord1[3*i+2]  # z distance from zero
        return energy


def main(args):
    if len(args) != 2:
        oechem.OEThrow.Usage("%s <input>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    mol = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, mol)
    vecCoords = oechem.OEDoubleArray(3*mol.GetMaxAtomIdx())
    mol.GetCoords(vecCoords)

    hermonic = Harmonic()
    hermonic.Setup(mol)
    optimizer = oeff.OEBFGSOpt()
    energy = optimizer(hermonic, vecCoords, vecCoords)
    oechem.OEThrow.Info("Optimized energy: %d" % energy)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
