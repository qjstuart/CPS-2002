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
# Split molecule file into N chunks or chunks of size N
#############################################################################
import os
import sys
from openeye import oechem


def NewOutputStream(outbase, ext, chunk):
    newname = outbase + ('_%07d' % chunk) + ext
    ofs = oechem.oemolostream()
    if not ofs.open(newname):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % newname)
    return ofs


def SplitNParts(ifs, nparts, countconfs, outbase, ext):
    # first read entire file to determine number of molecules
    molconfcount = 0
    for mol in ifs.GetOEMols():
        if countconfs:
            molconfcount += mol.NumConfs()
        else:
            molconfcount += 1
    ifs.rewind()

    chunksize, lft = divmod(molconfcount, nparts)
    if lft != 0:
        chunksize += 1
    chunk = 1
    count = 0

    ofs = NewOutputStream(outbase, ext, chunk)
    for mol in ifs.GetOEMols():
        if countconfs:
            count += mol.NumConfs()
        else:
            count += 1
        if count > chunksize:
            if chunk == lft:
                chunksize -= 1

            ofs.close()
            chunk += 1
            count = 1
            ofs = NewOutputStream(outbase, ext, chunk)

        oechem.OEWriteMolecule(ofs, mol)


def SplitChunk(ifs, chunksize, countconfs, outbase, ext):
    chunk = 1
    ofs = NewOutputStream(outbase, ext, chunk)

    count = 0
    for mol in ifs.GetOEMols():
        if count >= chunksize:
            ofs.close()
            count = 0
            chunk += 1
            ofs = NewOutputStream(outbase, ext, chunk)

        if countconfs:
            count += mol.NumConfs()
        else:
            count += 1
        oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    if not (itf.HasInt("-num") ^ itf.HasInt("-size")):
        oechem.OEThrow.Fatal("Number of chunks (-num) or the size of each chunk "
                             "(-size) must be specified and are mutually exclusive.")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    if (ifs.GetFormat() != oechem.OEFormat_OEB):
        ifs.SetConfTest(oechem.OEIsomericConfTest(False))
    outbase, ext = os.path.splitext(itf.GetString("-o"))

    if ext == '':
        oechem.OEThrow.Fatal("Failed to find file extension")

    if ext == '.gz':
        outbase, ext = os.path.splitext(outbase)
        ext = ext + '.gz'

    countconfs = itf.GetBool("-confs")

    if itf.HasInt("-num"):
        nparts = itf.GetInt("-num")
        SplitNParts(ifs, nparts, countconfs, outbase, ext)
    else:
        chunksize = itf.GetInt("-size")
        SplitChunk(ifs, chunksize, countconfs, outbase, ext)

#############################################################################


InterfaceData = """\
!BRIEF -num|-size [-i] <input> [-o] <output>
!PARAMETER -i 1
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o 2
  !TYPE string
  !REQUIRED true
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -num 3
  !TYPE int
  !BRIEF The number of chunks
!END
!PARAMETER -size 4
  !TYPE int
  !BRIEF The size of each chunk
!END
!PARAMETER -confs 5
  !TYPE bool
  !DEFAULT true
  !BRIEF Split by number of conformers not molecules
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
