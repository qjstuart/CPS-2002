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
# Count the number of chains,fragments,residues(water) and atoms in a protein
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def ResCount(ifs):
    nrmol = 0
    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        nrmol += 1
        nratom = 0
        nrwat = 0
        nrres = 0
        nrfrag = 0
        nrchain = 0
        if not oechem.OEHasResidues(mol):
            oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
        hv = oechem.OEHierView(mol)
        for chain in hv.GetChains():
            nrchain += 1
            for frag in chain.GetFragments():
                nrfrag += 1
                for res in frag.GetResidues():
                    nrres += 1
                    if oechem.OEGetResidueIndex(res.GetOEResidue()) == oechem.OEResidueIndex_HOH:
                        nrwat += 1
                    else:
                        for atom in res.GetAtoms():
                            nratom += 1

        print("===============================================")
        print("Molecule : %d Title: %s" % (nrmol, mol.GetTitle()))
        print("Chains   : %d" % nrchain)
        print("Fragments: %d" % nrfrag)
        print("Residues : %d (%d waters)" % (nrres, nrwat))
        print("Atoms    : %d" % nratom)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        oechem.OEThrow.Usage("rescount.py <infile>")
    ifs = oechem.oemolistream()
    if not ifs.open(sys.argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sys.argv[1])
    ResCount(ifs)
