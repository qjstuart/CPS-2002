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
from openeye import oezap


def PrintHeader(protTitle, ligTitle):
    oechem.OEThrow.Info("\nBinding Energy and Wall Clock Time for %s and %s" %
                        (protTitle, ligTitle))
    oechem.OEThrow.Info("%15s %15s %10s" % ("Focused?", "Energy(kT)", "Time(s)"))


def PrintInfo(focussed, energy, time):
    oechem.OEThrow.Info("%15s %15.3f %10.1f" % (focussed, energy, time))


def CalcBindingEnergy(zap, protein, ligand, cmplx):
    stopwatch = oechem.OEStopwatch()
    stopwatch.Start()

    ppot = oechem.OEFloatArray(protein.GetMaxAtomIdx())
    zap.SetMolecule(protein)
    zap.CalcAtomPotentials(ppot)
    proteinEnergy = 0.0
    for atom in protein.GetAtoms():
        proteinEnergy += ppot[atom.GetIdx()]*atom.GetPartialCharge()
    proteinEnergy *= 0.5

    lpot = oechem.OEFloatArray(ligand.GetMaxAtomIdx())
    zap.SetMolecule(ligand)
    zap.CalcAtomPotentials(lpot)
    ligandEnergy = 0.0
    for atom in ligand.GetAtoms():
        ligandEnergy += lpot[atom.GetIdx()]*atom.GetPartialCharge()
    ligandEnergy *= 0.5

    cpot = oechem.OEFloatArray(cmplx.GetMaxAtomIdx())
    zap.SetMolecule(cmplx)
    zap.CalcAtomPotentials(cpot)
    cmplxEnergy = 0.0
    for atom in cmplx.GetAtoms():
        cmplxEnergy += cpot[atom.GetIdx()]*atom.GetPartialCharge()
    cmplxEnergy *= 0.5

    energy = cmplxEnergy - ligandEnergy - proteinEnergy
    time = stopwatch.Elapsed()

    if zap.IsFocusTargetSet():
        focused = "Yes"
    else:
        focused = "No"

    PrintInfo(focused, energy, time)


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <protein> <ligand>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, protein)

    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    ligand = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, ligand)

    oechem.OEAssignBondiVdWRadii(protein)
    oechem.OEMMFFAtomTypes(protein)
    oechem.OEMMFF94PartialCharges(protein)

    oechem.OEAssignBondiVdWRadii(ligand)
    oechem.OEMMFFAtomTypes(ligand)
    oechem.OEMMFF94PartialCharges(ligand)

    cmplx = oechem.OEGraphMol(protein)
    oechem.OEAddMols(cmplx, ligand)

    epsin = 1.0
    spacing = 0.5
    zap = oezap.OEZap()
    zap.SetInnerDielectric(epsin)
    zap.SetGridSpacing(spacing)

    PrintHeader(protein.GetTitle(), ligand.GetTitle())

    CalcBindingEnergy(zap, protein, ligand, cmplx)
    zap.SetFocusTarget(ligand)
    CalcBindingEnergy(zap, protein, ligand, cmplx)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
