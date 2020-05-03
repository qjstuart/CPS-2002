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


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))

    pfs = oechem.oemolistream()
    if not pfs.open(itf.GetString("-protein")):
        oechem.OEThrow.Fatal("Unable to open %s for reading", itf.GetString("-protein"))

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-outl")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-outl"))

    opfs = oechem.oemolostream()
    if not opfs.open(itf.GetString("-outp")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-outp"))

    ligand = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, ligand)
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(pfs, protein)

    # Szybki options
    opts = oeszybki.OESzybkiOptions()
    opts.SetRunType(oeszybki.OERunType_CartesiansOpt)
    opts.GetOptOptions().SetMaxIter(2000)
    opts.GetOptOptions().SetGradTolerance(1e-6)
    opts.GetGeneralOptions().SetForceFieldType(oeszybki.OEForceFieldType_MMFF94S)
    opts.GetProteinOptions().SetProteinFlexibilityType(oeszybki.OEProtFlex_SideChainsList)
    opts.GetProteinOptions().SetProteinElectrostaticModel(
                             oeszybki.OEProteinElectrostatics_ExactCoulomb)

    res_num = []
    for res in itf.GetStringList('-residues'):
        intres = None
        try:
            intres = int(res)
        except ValueError:
            print('Illegal residue value: {}'.format(res))

        if intres is None:
            continue
        res_num.append(intres)

    for i in res_num:
        for atom in protein.GetAtoms():
            residue = oechem.OEAtomGetResidue(atom)
            if(residue.GetResidueNumber() == i):
                opts.AddFlexibleResidue(residue)
                break

    sz = oeszybki.OESzybki(opts)
    sz.SetProtein(protein)
    result = oeszybki.OESzybkiResults()
    sz(ligand, result)
    sz.GetProtein(protein)
    oechem.OEWriteMolecule(opfs, protein)
    oechem.OEWriteMolecule(ofs, ligand)

    return 0


Interface = """
!BRIEF -in ligand -protein protein -outl output_ligand -outp output_protein -residues r1 r2 ... rn
!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input ligand file name.
!END

!PARAMETER -protein
  !TYPE string
  !REQUIRED true
  !BRIEF Input protein file name.
!END

!PARAMETER -outl
  !TYPE string
  !REQUIRED true
  !BRIEF Output ligand file name.
!END

!PARAMETER -outp
  !TYPE string
  !REQUIRED true
  !BRIEF Output protein file name.
!END

!PARAMETER -residues
  !TYPE string
  !LIST true
  !REQUIRED true
  !BRIEF List of residues numbers to be optimized along with the ligand
!END

"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
