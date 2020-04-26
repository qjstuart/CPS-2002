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


def Output(mol, apot, showAtomTable):
    print("Title: %s" % mol.GetTitle())
    if showAtomTable:
        print("Atom potentials")
        print("Index  Elem    Charge     Potential")

    energy = 0.0
    for atom in mol.GetAtoms():
        energy += atom.GetPartialCharge()*apot[atom.GetIdx()]
        if showAtomTable:
            print("%3d     %2s     %6.3f     %8.3f" %
                  (atom.GetIdx(),
                   oechem.OEGetAtomicSymbol(atom.GetAtomicNum()),
                   atom.GetPartialCharge(),
                   apot[atom.GetIdx()]))

    print("Sum of {Potential * Charge over all atoms * 0.5} in kT = %f\n" %
          (0.5*energy))


def CalcAtomPotentials(itf):
    mol = oechem.OEGraphMol()

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))

    oechem.OEReadMolecule(ifs, mol)
    oechem.OEAssignBondiVdWRadii(mol)

    if not itf.GetBool("-file_charges"):
        oechem.OEMMFFAtomTypes(mol)
        oechem.OEMMFF94PartialCharges(mol)

    zap = oezap.OEZap()
    zap.SetMolecule(mol)
    zap.SetInnerDielectric(itf.GetFloat("-epsin"))
    zap.SetBoundarySpacing(itf.GetFloat("-boundary"))
    zap.SetGridSpacing(itf.GetFloat("-grid_spacing"))

    showAtomTable = itf.GetBool("-atomtable")
    calcType = itf.GetString("-calc_type")
    if calcType == "default":
        apot = oechem.OEFloatArray(mol.GetMaxAtomIdx())
        zap.CalcAtomPotentials(apot)
        Output(mol, apot, showAtomTable)

    elif calcType == "solvent_only":
        apot = oechem.OEFloatArray(mol.GetMaxAtomIdx())
        zap.CalcAtomPotentials(apot)

        apot2 = oechem.OEFloatArray(mol.GetMaxAtomIdx())
        zap.SetOuterDielectric(zap.GetInnerDielectric())
        zap.CalcAtomPotentials(apot2)

        # find the differences
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            apot[idx] -= apot2[idx]

        Output(mol, apot, showAtomTable)

    elif calcType == "remove_self":
        apot = oechem.OEFloatArray(mol.GetMaxAtomIdx())
        zap.CalcAtomPotentials(apot, True)
        Output(mol, apot, showAtomTable)

    elif calcType == "coulombic":
        epsin = itf.GetFloat("-epsin")
        x = oezap.OECoulombicSelfEnergy(mol, epsin)
        print("Coulombic Assembly Energy")
        print("  = Sum of {Potential * Charge over all atoms * 0.5} in kT = %f" % x)
        apot = oechem.OEFloatArray(mol.GetMaxAtomIdx())
        oezap.OECoulombicAtomPotentials(mol, epsin, apot)
        Output(mol, apot, showAtomTable)

    return 0


def SetupInterface(itf, InterfaceData):
    oechem.OEConfigure(itf, InterfaceData)
    if oechem.OECheckHelp(itf, sys.argv):
        return False
    if not oechem.OEParseCommandLine(itf, sys.argv):
        return False
    return True


def main(InterfaceData):
    itf = oechem.OEInterface()
    if not SetupInterface(itf, InterfaceData):
        return 1

    return CalcAtomPotentials(itf)


InterfaceData = """
#zap_atompot interface definition

!PARAMETER -in
  !TYPE string
  !BRIEF Input molecule file.
  !REQUIRED true
  !KEYLESS 1
!END

!PARAMETER -file_charges
  !TYPE bool
  !DEFAULT false
  !BRIEF Use partial charges from input file rather than calculating with MMFF.
!END

!PARAMETER -calc_type
  !TYPE string
  !DEFAULT default
  !LEGAL_VALUE default
  !LEGAL_VALUE solvent_only
  !LEGAL_VALUE remove_self
  !LEGAL_VALUE coulombic
  !LEGAL_VALUE breakdown
  !BRIEF Choose type of atom potentials to calculate
!END

!PARAMETER -atomtable
  !TYPE bool
  !DEFAULT false
  !BRIEF Output a table of atom potentials
!END

!PARAMETER -epsin
  !TYPE float
  !BRIEF Inner dielectric
  !DEFAULT 1.0
  !LEGAL_RANGE 0.0 100.0
!END

!PARAMETER -grid_spacing
  !TYPE float
  !DEFAULT 0.5
  !BRIEF Spacing between grid points (Angstroms)
  !LEGAL_RANGE 0.1 2.0
!END

!PARAMETER -boundary
  !ALIAS -buffer
  !TYPE float
  !DEFAULT 2.0
  !BRIEF Extra buffer outside extents of molecule.
  !LEGAL_RANGE 0.1 10.0
!END
"""

if __name__ == "__main__":
    sys.exit(main(InterfaceData))
