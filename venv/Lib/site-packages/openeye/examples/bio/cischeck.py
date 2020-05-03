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
# Count the number of cis amide (omega) residue bonds in a protein
#############################################################################
from __future__ import print_function
import sys
import math
from openeye import oechem


def CisCheck(ifs):
    nrmol = 0
    nrcis = 0
    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        nrmol += 1
        print("===========================================================")
        print("Molecule: %s   Title: %s" % (nrmol, mol.GetTitle()))
        if not oechem.OEHasResidues(mol):
            oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
        hv = oechem.OEHierView(mol)
        resiter = oechem.ConstOEHierResidueIter()
        resiter = hv.GetResidues()
        while (resiter.IsValid()):
            res = resiter.Target()
            resiter.Next()
            if not oechem.OEIsStandardProteinResidue(res):
                continue
            torsion = oechem.OEGetTorsion(res, oechem.OEProtTorType_Omega)
            if torsion != -100.0:
                if torsion < math.pi/2.0 and torsion > -math.pi/2.0:
                    if resiter.IsValid():
                        nextres = resiter.Target()
                        oenextres = nextres.GetOEResidue()
                        if oechem.OEGetResidueIndex(oenextres) == oechem.OEResidueIndex_PRO:
                            continue
                    nrcis += 1
                    oeres = res.GetOEResidue()
                    print("%s %s %2d omega torsion = %.2f degree" % (oeres.GetName(),
                                                                     oeres.GetChainID(),
                                                                     oeres.GetResidueNumber(),
                                                                     torsion*oechem.cvar.Rad2Deg))
        print(" %d cis amide bond(s) identified\n" % nrcis)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        oechem.OEThrow.Usage("cischeck.py <infile>")
    ifs = oechem.oemolistream()
    if not ifs.open(sys.argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sys.argv[1])
    CisCheck(ifs)
