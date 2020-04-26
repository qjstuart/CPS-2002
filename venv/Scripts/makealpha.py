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

#############################################################################
# Set phi, psi and chis torsion angles in a protein
#############################################################################
from __future__ import print_function
import sys
import math
from openeye import oechem


def MakeAlpha(ifs, ofs):
    phival = math.pi / -3.0
    psival = math.pi / -3.0
    chival = math.pi
    nrphis = 0
    nrpsis = 0
    nrchis = 0
    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        if not oechem.OEHasResidues(mol):
            oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
        # remove cross-links
        for bond in mol.GetBonds():
            if bond.GetBgn().GetAtomicNum() == oechem.OEElemNo_S and \
               bond.GetEnd().GetAtomicNum() == oechem.OEElemNo_S:
                mol.DeleteBond(bond)

        oechem.OEFindRingAtomsAndBonds(mol)
        hv = oechem.OEHierView(mol)
        for res in hv.GetResidues():
            if not oechem.OEIsStandardProteinResidue(res):
                continue

            # set psi and phi angles
            if not oechem.OESetTorsion(res, oechem.OEProtTorType_Phi, phival):
                oeres = res.GetOEResidue()
                print("Unable to set phi for %s %d" % (oeres.GetName(),
                                                       oeres.GetResidueNumber()))
            else:
                nrphis += 1

            if not oechem.OESetTorsion(res, oechem.OEProtTorType_Psi, psival):
                oeres = res.GetOEResidue()
                print("Unable to set psi for %s %d" % (oeres.GetName(),
                                                       oeres.GetResidueNumber()))
            else:
                nrpsis += 1

            # set chis
            if oechem.OEGetResidueIndex(res.GetOEResidue().GetName()) == oechem.OEResidueIndex_PRO:
                continue  # It does not make sense to set Proline chi angles to 180

            for chi in oechem.OEGetChis(res):
                if not oechem.OESetTorsion(res, chi, chival):
                    oeres = res.GetOEResidue()
                    print("Unable to set chi %s for %s %d" % (oechem.OEGetProteinTorsionName(chi),
                                                              oeres.GetName(),
                                                              oeres.GetResidueNumber()))
                else:
                    nrchis += 1
        oechem.OEWriteMolecule(ofs, mol)

    print(nrphis, " phi  torsion angle set to ", phival * oechem.cvar.Rad2Deg)
    print(nrpsis, " psi  torsion angle set to ", psival * oechem.cvar.Rad2Deg)
    print(nrchis, " chis torsion angle set to ", chival * oechem.cvar.Rad2Deg)


def main(argv=[__name__]):
    if len(sys.argv) != 3:
        oechem.OEThrow.Usage("makealpha.py <infile> <outfile>")
    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    ofs = oechem.oemolostream()
    if not ofs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    MakeAlpha(ifs, ofs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
