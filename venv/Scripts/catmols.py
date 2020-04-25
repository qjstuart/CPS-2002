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
# This program concatenates molecules into one file.
# It can be useful for generating ROCS queries or reattach ligands to an
# protein structure
#############################################################################
import sys
from openeye import oechem


def CatMols(infnames, outfname):
    omol = oechem.OEGraphMol()
    for fname in infnames:
        ifs = oechem.oemolistream()
        if ifs.open(fname):
            for imol in ifs.GetOEGraphMols():
                oechem.OEAddMols(omol, imol)
        else:
            oechem.OEThrow.Fatal("Unable to open %s for reading" % fname)

    ofs = oechem.oemolostream()
    if not ofs.open(outfname):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outfname)

    oechem.OEWriteMolecule(ofs, omol)


Interface = """
!BRIEF -i <infile1> [<infile2>...] -o <outfile>
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !LIST true
  !REQUIRED true
  !BRIEF input file name(s)
!END
!PARAMETER -o
  !ALIAS -out
  !TYPE string
  !REQUIRED true
  !BRIEF output file name
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)

    CatMols(itf.GetStringList("-i"), itf.GetString("-o"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
