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
# Generate canonical smiles of various flavors
#############################################################################
import sys
from openeye import oechem

#############################################################################
# To create unique Kekule smiles, must reperceive bond orders from
# scratch to avoid arbitrary non-deterministic variations, e.g.,
# CC1=C(O)C=CC=C1 vs. CC1=CC=CC=C1O
# This is why oechem.OESMILESFlag_Kekule is not sufficient and not used.
#############################################################################


def CanSmi(mol, isomeric, kekule):
    oechem.OEFindRingAtomsAndBonds(mol)
    oechem.OEAssignAromaticFlags(mol, oechem.OEAroModel_OpenEye)
    smiflag = oechem.OESMILESFlag_Canonical
    if isomeric:
        smiflag |= oechem.OESMILESFlag_ISOMERIC

    if kekule:
        for bond in mol.GetBonds(oechem.OEIsAromaticBond()):
            bond.SetIntType(5)
        oechem.OECanonicalOrderAtoms(mol)
        oechem.OECanonicalOrderBonds(mol)
        oechem.OEClearAromaticFlags(mol)
        oechem.OEKekulize(mol)

    smi = oechem.OECreateSmiString(mol, smiflag)
    return smi


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    isomeric = itf.GetBool("-isomeric")
    kekule = itf.GetBool("-kekule")
    from3d = itf.GetBool("-from3d")

    if from3d:
        isomeric = True

    ifs = oechem.oemolistream()
    ifile = itf.GetString("-i")
    if not ifs.open(ifile):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifile)

    if itf.HasString("-o"):
        ofile = itf.GetString("-o")
        try:
            ofs = open(ofile, 'w')
        except Exception:
            oechem.OEThrow.Fatal("Unable to open %s for writing" % ofile)
    else:
        ofs = sys.stdout

    mol = oechem.OEGraphMol()
    while oechem.OEReadMolecule(ifs, mol):
        if from3d:
            oechem.OE3DToInternalStereo(mol)
        smi = CanSmi(mol, isomeric, kekule)
        if mol.GetTitle():
            smi += (" %s" % mol.GetTitle())
        ofs.write("%s\n" % smi)


InterfaceData = """\
!BRIEF [options] [-i] <input> [[-o] <output>]
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
  !BRIEF output file name
  !KEYLESS 2
!END
!PARAMETER -isomeric
  !TYPE bool
  !DEFAULT false
  !BRIEF generate isomeric smiles
!END
!PARAMETER -from3d
  !TYPE bool
  !DEFAULT false
  !BRIEF perceive stereo from 3D coords
!END
!PARAMETER -kekule
  !TYPE bool
  !DEFAULT false
  !BRIEF generate kekule form
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
