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
# Extract compound(s) from a file based on molecule title
#############################################################################
import sys

try:
    set()
except NameError:
    from sets import Set as set
from openeye import oechem


def MolExtract(ifs, ofs, nameset):
    for mol in ifs.GetOEMols():
        title = mol.GetTitle()
        if title in nameset:
            oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)
    haslist = itf.HasString("-list")
    hastitle = itf.HasString("-title")
    if not (haslist ^ hastitle):
        oechem.OEThrow.Usage("Must give either -list or -title")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    # collect names
    nameset = set()
    if itf.HasString("-list"):
        try:
            lfs = open(itf.GetString("-list"))
        except IOError:
            oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-list"))
        for name in lfs.readlines():
            name = name.strip()
            nameset.add(name)
    elif itf.HasString("-title"):
        nameset.add(itf.GetString("-title"))

    if len(nameset) == 0:
        oechem.OEThrow.Fatal("No titles requested")

    MolExtract(ifs, ofs, nameset)


InterfaceData = """\
!BRIEF -title title | -list <moltitles.file> [-i] <input> [-o] <output>
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !ALIAS -out
  !TYPE string
  !REQUIRED true
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -title
  !ALIAS -t
  !TYPE string
  !BRIEF Single mol title to extract
!END
!PARAMETER -list
  !ALIAS -l
  !TYPE string
  !BRIEF List file of mol titles to extract
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
