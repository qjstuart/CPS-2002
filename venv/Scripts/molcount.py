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
# Counts molecule (and conformers) in input files
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def PrintConfInfo(nconfs, nmols):
    print("Total # of conformers:  ", nconfs)
    avg = 0
    if nmols:
        avg = float(nconfs) / nmols
    print("Average # of conformers:", avg)


def MolCount(ifs, fname, conffrag):
    nummols = 0
    numconfs = 0
    for mol in ifs.GetOEMols():
        nummols += 1
        if conffrag:
            numconfs += mol.NumConfs()

    print("%s contains %d molecule(s)." % (fname, nummols))

    if conffrag:
        PrintConfInfo(numconfs, nummols)
        print("-----------------------------------------------------------")

    return nummols, numconfs


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)
    conffrag = itf.GetBool("-conf")

    totmols = 0
    totconfs = 0
    for fname in itf.GetStringList("-i"):
        ifs = oechem.oemolistream()
        if not ifs.open(fname):
            oechem.OEThrow.Warning("Unable to open %s for reading" % fname)
            continue

        nummol, numconfs = MolCount(ifs, fname, conffrag)
        totmols += nummol
        totconfs += numconfs

    print("===========================================================")
    print("Total %d molecules" % totmols)
    if conffrag:
        PrintConfInfo(totconfs, totmols)


Interface = """
!BRIEF [-conf] [-i] <infile1> [<infile2>...]
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !LIST true
  !REQUIRED true
  !BRIEF Input file name(s)
  !KEYLESS 1
!END
!PARAMETER -conf
  !ALIAS -c
  !TYPE bool
  !DEFAULT false
  !BRIEF Count conformers
!END
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
