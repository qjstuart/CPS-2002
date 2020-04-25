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
# Print the phi and psi rotatable angles for each residues in a protein
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def ShowPhiPsi(ifs):
    nrmol = 0
    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        nrmol += 1
        print("================================================")
        print("Molecule: %d  Title: %s" % (nrmol, mol.GetTitle()))

        if not oechem.OEHasResidues(mol):
            oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
        hv = oechem.OEHierView(mol)

        for res in hv.GetResidues():
            if not oechem.OEIsStandardProteinResidue(res):
                continue

            phi = oechem.OEGetPhi(res)
            psi = oechem.OEGetPsi(res)

            oeres = res.GetOEResidue()
            print("  %s %s %d (PHI=%.2f, PSI=%.2f)" % (oeres.GetName(),
                                                       oeres.GetChainID(),
                                                       oeres.GetResidueNumber(),
                                                       phi, psi))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        oechem.OEThrow.Usage("phipsi.py <infile>")
    ifs = oechem.oemolistream()
    if not ifs.open(sys.argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sys.argv[1])
    ShowPhiPsi(ifs)
