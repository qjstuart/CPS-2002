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
# Perform sequence alignment of two proteins and print alignment with RMSD
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def SeqAlign(ref, fit, ofs):
    sa = oechem.OEGetAlignment(ref, fit)
    print()
    print("Alignment of %s to %s" % (fit.GetTitle(), ref.GetTitle()))
    print()
    print("  Method: %s" % oechem.OEGetAlignmentMethodName(sa.GetMethod()))
    print("  Gap   : %d" % sa.GetGap())
    print("  Extend: %d" % sa.GetExtend())
    print("  Score : %d" % sa.GetScore())
    print()

    oss = oechem.oeosstream()
    oechem.OEWriteAlignment(oss, sa)
    print(oss.str().decode("UTF-8"))

    onlyCAlpha = True
    overlay = True
    rot = oechem.OEDoubleArray(9)
    trans = oechem.OEDoubleArray(3)
    rmsd = oechem.OERMSD(ref, fit, sa, onlyCAlpha, overlay, rot, trans)
    print("  RMSD = %.1f" % rmsd)
    oechem.OERotate(fit, rot)
    oechem.OETranslate(fit, trans)
    oechem.OEWriteMolecule(ofs, fit)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        oechem.OEThrow.Usage("seqalign.py <inmol1> <inmol2> <outfile>")

    ifs = oechem.oemolistream()
    if not ifs.open(sys.argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sys.argv[1])
    ref = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, ref)
    ifs.close()

    if not ifs.open(sys.argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % sys.argv[2])
    fit = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, fit)
    ifs.close()

    ofs = oechem.oemolostream()
    if not ofs.open(sys.argv[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % sys.argv[3])

    SeqAlign(ref, fit, ofs)
