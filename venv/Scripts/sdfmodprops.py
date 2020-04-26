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
# Modifies the SD data of a set of input molecules by clearing all tags,
# defining which tags to keep or defining which tags to remove
#############################################################################
import sys
from openeye import oechem


def ClearProps(ifs, ofs):
    for mol in ifs.GetOEGraphMols():
        oechem.OEClearSDData(mol)
        oechem.OEWriteMolecule(ofs, mol)


def KeepProps(proplist, ifs, ofs):
    for mol in ifs.GetOEGraphMols():
        for dp in oechem.OEGetSDDataPairs(mol):
            if dp.GetTag() not in proplist:
                oechem.OEDeleteSDData(mol, dp.GetTag())
        oechem.OEWriteMolecule(ofs, mol)


def RemoveProps(proplist, ifs, ofs):
    for mol in ifs.GetOEGraphMols():
        for tag in proplist:
            oechem.OEDeleteSDData(mol, tag)
        oechem.OEWriteMolecule(ofs, mol)


def ModProps(itf, ifs, ofs):
    proplist = []
    if itf.HasString("-keep"):
        for prop in itf.GetStringList("-keep"):
            proplist.append(prop)
        KeepProps(proplist, ifs, ofs)
    elif itf.HasString("-remove"):
        for prop in itf.GetStringList("-remove"):
            proplist.append(prop)
        RemoveProps(proplist, ifs, ofs)
    elif itf.GetBool("-clearAll"):
        ClearProps(ifs, ofs)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    haskeep = itf.HasString("-keep")
    hasremove = itf.HasString("-remove")
    hasclear = itf.GetBool("-clearAll")

    numoption = 0
    for hasoption in [haskeep, hasremove, hasclear]:
        if hasoption:
            numoption += 1

    if numoption != 1:
        oechem.OEThrow.Usage("Need to pick one from -keep, -remove, or -clearAll")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))
    if not oechem.OEIsSDDataFormat(ifs.GetFormat()):
        oechem.OEThrow.Fatal("Only works for input file formats that support SD data (sdf,oeb,csv)")

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))
    if not oechem.OEIsSDDataFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Only works for output file formats that support SD data \
                             (sdf,oeb,csv)")

    ModProps(itf, ifs, ofs)


InterfaceData = """
!BRIEF [-remove] <prop1 prop2...> [-keep] <prop1 prop2...> [-clearAll] -i <input> -o <output>
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !END
!PARAMETER -o
  !ALIAS -out
  !TYPE string
  !REQUIRED true
  !BRIEF Output file name
  !END
!PARAMETER -keep
  !ALIAS -k
  !TYPE string
  !LIST true
  !BRIEF SD tags to be kept
  !END
!PARAMETER -remove
  !ALIAS -r
  !TYPE string
  !LIST true
  !BRIEF SD tags to be removed
  !END
!PARAMETER -clearAll
  !ALIAS -c
  !TYPE bool
  !DEFAULT false
  !BRIEF Removes all SD tags
  !END
!END
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
