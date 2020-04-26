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
# Filter out molecules by their molecular weight or heavy atom count
#############################################################################
import sys
from openeye import oechem


def IsBetween(min, max, val):
    if min <= val <= max:
        return True
    return False


def IsMoleculeInHeavyAtomCountRange(min, max, mol):
    count = oechem.OECount(mol, oechem.OEIsHeavy())
    return IsBetween(min, max, count)


def IsMoleculeInMolWtRange(min, max, mol):
    molwt = oechem.OECalculateMolecularWeight(mol)
    return IsBetween(min, max, molwt)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    ofs = oechem.oemolostream(".ism")
    if itf.HasString("-o"):
        if not ofs.open(itf.GetString("-o")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    minhac = float("-inf")
    if itf.HasInt("-minhac"):
        minhac = itf.GetInt("-minhac")
    maxhac = float("inf")
    if itf.HasInt("-maxhac"):
        maxhac = itf.GetInt("-maxhac")
    minwt = float("-inf")
    if itf.HasDouble("-minwt"):
        minwt = itf.GetDouble("-minwt")
    maxwt = float("inf")
    if itf.HasDouble("-maxwt"):
        maxwt = itf.GetDouble("-maxwt")

    for mol in ifs.GetOEMols():
        if not IsMoleculeInHeavyAtomCountRange(minhac, maxhac, mol):
            continue
        if not IsMoleculeInMolWtRange(minwt, maxwt, mol):
            continue

        oechem.OEWriteMolecule(ofs, mol)


InterfaceData = """
!BRIEF [-minhac <num>] [-maxhac <num>] [-minwt <num>] [-maxwt <num>] [-i] <input> [[-o] <output>]
!PARAMETER -i
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !TYPE string
  !REQUIRED false
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -minhac
  !TYPE int
  !REQUIRED false
  !BRIEF minimum heavy atom count
!END
!PARAMETER -maxhac
  !TYPE int
  !REQUIRED false
  !BRIEF maximum heavy atom count
!END
!PARAMETER -minwt
  !TYPE double
  !REQUIRED false
  !BRIEF minimum molecular weight
!END
!PARAMETER -maxwt
  !TYPE double
  !REQUIRED false
  !BRIEF maximum molecular weight
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
