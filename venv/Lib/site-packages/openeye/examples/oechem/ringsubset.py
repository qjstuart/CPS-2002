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

#######################################################################
# Extracting rings/ring systems from input molecules
#######################################################################
import sys
from openeye import oechem


def RingSubSet(ifs, ofs, exo):
    for mol in ifs.GetOEGraphMols():
        submol = oechem.OEGraphMol()
        adjustHcount = True
        if exo:
            isinring = oechem.OEAtomIsInRing()
            isexo = oechem.OEIsNonRingAtomDoubleBondedToRing()
            includeexo = oechem.OEOrAtom(isinring, isexo)
            oechem.OESubsetMol(submol, mol, includeexo, adjustHcount)
        else:
            oechem.OESubsetMol(submol, mol, oechem.OEAtomIsInRing(), adjustHcount)
        submol.SetTitle(mol.GetTitle() + "_rings")
        if submol.NumAtoms() != 0:
            oechem.OEWriteMolecule(ofs, submol)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    exo_dbl_bonds = itf.GetBool("-exo")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    ofs = oechem.oemolostream(".ism")
    if itf.HasString("-o"):
        if not ofs.open(itf.GetString("-o")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))
    RingSubSet(ifs, ofs, exo_dbl_bonds)


InterfaceData = """
!BRIEF [-exo] [-i] <infile> [[-o] <outfile>]
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !REQUIRED true
  !BRIEF input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !ALIAS -out
  !TYPE string
  !REQUIRED false
  !BRIEF output file name
  !KEYLESS 2
!END
!PARAMETER -exo
  !TYPE bool
  !DEFAULT true
  !BRIEF Include non-ring atoms double bonded to a ring
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
