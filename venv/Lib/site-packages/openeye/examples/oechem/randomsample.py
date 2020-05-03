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
#  Randomly reorder molecules and optionally obtain a random subset
#############################################################################
import sys
from random import Random
from openeye import oechem


def LoadDatabase(ifs, mlist, count):
    for pos, mol in enumerate(ifs.GetOEMols()):
        newmol = oechem.OEMol(mol, oechem.OEMCMolType_OEDBMCMol)
        newmol.Compress()
        mlist.append(newmol)
        if pos + 1 == count:
            break


def WriteDatabase(ofs, mlist, size):
    for mol in mlist[:size]:
        mol.UnCompress()
        oechem.OEWriteMolecule(ofs, mol)
        mol.Clear()


def RandomizePercent(ifs, ofs, percent, rand):
    mlist = []
    LoadDatabase(ifs, mlist, 0)

    rand.shuffle(mlist)

    size = len(mlist)
    size = int(percent * 0.01 * size)
    if size < 1:
        size = 1
    WriteDatabase(ofs, mlist, size)


def Randomize(ifs, ofs, rand):
    wholedb = 100
    RandomizePercent(ifs, ofs, wholedb, rand)


def RandomizeN(ifs, ofs, count, rand):
    mlist = []
    LoadDatabase(ifs, mlist, count)

    for pos, mol in enumerate(ifs.GetOEMols()):
        if float(count / float(count + pos + 1)) > rand.random():
            idx = int(float(count) * rand.random())
            newmol = oechem.OEMol(mol, oechem.OEMCMolType_OEDBMCMol)
            newmol.Compress()
            mlist[idx] = newmol

    rand.shuffle(mlist)
    WriteDatabase(ofs, mlist, count)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    if itf.HasFloat("-p") and itf.HasInt("-n"):
        oechem.OEThrow.Usage("Give only one option, -p or -n")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    ofs = oechem.oemolostream(".ism")
    if itf.HasString("-o"):
        if not ofs.open(itf.GetString("-o")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    if itf.HasInt("-seed"):
        rand = Random(itf.GetInt("-seed"))
    else:
        rand = Random()

    if itf.HasInt("-n"):
        RandomizeN(ifs, ofs, itf.GetInt("-n"), rand)
    elif itf.HasFloat("-p"):
        RandomizePercent(ifs, ofs, itf.GetFloat("-p"), rand)
    else:
        Randomize(ifs, ofs, rand)


InterfaceData = """
!BRIEF [-seed <int>] [-n <number>] [-p <percent>] [-i] <input> [-o] <output>
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
!PARAMETER -p
  !TYPE float
  !REQUIRED false
  !BRIEF Percentage of output molecules
!END
!PARAMETER -n
  !TYPE int
  !REQUIRED false
  !BRIEF Number of output molecules
!END
!PARAMETER -seed
  !TYPE int
  !REQUIRED false
  !BRIEF Integer value for random seed, default is system time
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
