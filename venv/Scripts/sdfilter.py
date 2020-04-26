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
# Filter molecules by SD data
#############################################################################
import sys
from openeye import oechem


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)
    if not (itf.HasDouble("-min") or itf.HasDouble("-max")):
        oechem.OEThrow.Fatal("Please set a filter value with -min or -max")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    if not oechem.OEIsSDDataFormat(ifs.GetFormat()):
        oechem.OEThrow.Fatal("Only works for input file formats that support SD data (sdf,oeb,csv)")

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-i"))

    if not oechem.OEIsSDDataFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Only works for output file formats that support SD data \
                             (sdf,oeb,csv)")

    tag = itf.GetString("-tag")

    minval = float("-inf")
    if itf.HasDouble("-min"):
        minval = itf.GetDouble("-min")

    maxval = float("inf")
    if itf.HasDouble("-max"):
        maxval = itf.GetDouble("-max")

    for mol in ifs.GetOEGraphMols():
        if not oechem.OEHasSDData(mol, tag):
            oechem.OEThrow.Warning(
                "Unable to find %s tag on %s" % (tag, mol.GetTitle()))
            continue

        value = oechem.OEGetSDData(mol, tag)
        try:
            tagvalue = float(value)
        except ValueError:
            oechem.OEThrow.Warning("Failed to convert (%s) to a number in %s" %
                                   (value, mol.GetTitle()))
            continue

        if tagvalue < minval:
            continue

        if tagvalue > maxval:
            continue

        oechem.OEWriteMolecule(ofs, mol)


InterfaceData = """
!BRIEF -i <input> -o <output> -tag <name> [-min <num>] [-max <num>]
!PARAMETER -i
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !TYPE string
  !REQUIRED true
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -tag
  !TYPE string
  !REQUIRED true
  !BRIEF SD tag
!END
!PARAMETER -min
  !TYPE double
  !REQUIRED false
  !BRIEF minimum value of SD tag
!END
!PARAMETER -max
  !TYPE double
  !REQUIRED false
  !BRIEF maximum value of SD tag
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
