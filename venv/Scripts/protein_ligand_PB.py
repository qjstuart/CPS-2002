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
from openeye import oeszybki


def main(args):
    if len(args) != 4:
        oechem.OEThrow.Usage("%s ligand_file protein_file output_file (SDF or OEB)" % args[0])

    lfs = oechem.oemolistream()
    if not lfs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    pfs = oechem.oemolistream()
    if not pfs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[2])

    ofs = oechem.oemolostream()
    if not ofs.open(args[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[3])

    if not oechem.OEIsSDDataFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Output file does not support SD data used by this example")

    # Szybki options for VdW-Coulomb calculations
    optsC = oeszybki.OESzybkiOptions()
    optsC.GetProteinOptions().SetProteinElectrostaticModel(
                              oeszybki.OEProteinElectrostatics_ExactCoulomb)
    optsC.SetRunType(oeszybki.OERunType_CartesiansOpt)

    # Szybki options for PB calculations
    optsPB = oeszybki.OESzybkiOptions()
    optsPB.GetProteinOptions().SetProteinElectrostaticModel(
                               oeszybki.OEProteinElectrostatics_SolventPBForces)
    optsPB.SetRunType(oeszybki.OERunType_SinglePoint)

    # Szybki objects
    szC = oeszybki.OESzybki(optsC)
    szPB = oeszybki.OESzybki(optsPB)

    # read and setup protein
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(pfs, protein)
    szC.SetProtein(protein)
    szPB.SetProtein(protein)

    terms = set([oeszybki.OEPotentialTerms_ProteinLigandInteraction,
                 oeszybki.OEPotentialTerms_VdWProteinLigand,
                 oeszybki.OEPotentialTerms_CoulombProteinLigand,
                 oeszybki.OEPotentialTerms_ProteinDesolvation,
                 oeszybki.OEPotentialTerms_LigandDesolvation,
                 oeszybki.OEPotentialTerms_SolventScreening])

    # process molecules
    for mol in lfs.GetOEMols():

        # optimize mol
        if not list(szC(mol)):
            oechem.OEThrow.Warning("No results processing molecule: %s" % mol.GetTitle())
            continue

        # do single point with better electrostatics
        for conf, results in zip(mol.GetConfs(), szPB(mol)):
            for i in terms:
                strEnergy = ("%9.4f" % results.GetEnergyTerm(i))
                oechem.OEAddSDData(conf, oeszybki.OEGetEnergyTermName(i), strEnergy)

        oechem.OEWriteMolecule(ofs, mol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
