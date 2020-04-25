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
# Swap ambiguous isoelectronic residue atoms in a protein
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def SwapAIERes(ifs, ofs, chainid, resname, resnum):
    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        if not oechem.OEHasResidues(mol):
            oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
        hv = oechem.OEHierView(mol)
        res = hv.GetResidue(chainid, resname, resnum)
        if res.GetOEResidue().GetName() is None:
            oechem.OEThrow.Fatal("Failed to find residue")
        if not oechem.OESwapAIEResidueAtoms(mol, res):
            print("failed to swap %s %d" % (resname, resnum))
        oechem.OEWriteMolecule(ofs, mol)


if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        oechem.OEThrow.Usage("swapaieres.py <resname> [chain] <resnum> <infile> <outfile>\n"
                             "example: swapaieres.py ASN A 23 dhfr.pdb out.pdb\n"
                             "Chain ID required if the residue has a chain ID")

    resname = sys.argv[1]
    chainid = " "
    if len(sys.argv) == 5:
        resnum = int(sys.argv[2])
        infile = sys.argv[3]
        outfile = sys.argv[4]
    elif len(sys.argv) == 6:
        chainid = sys.argv[2]
        resnum = int(sys.argv[3])
        infile = sys.argv[4]
        outfile = sys.argv[5]

    ifs = oechem.oemolistream()
    if not ifs.open(infile):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % infile)
    ofs = oechem.oemolostream()
    if not ofs.open(outfile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfile)
    SwapAIERes(ifs, ofs, chainid, resname, resnum)
