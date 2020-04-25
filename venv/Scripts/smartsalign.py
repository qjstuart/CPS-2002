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
# Align two compounds based on smarts match
#############################################################################
import sys
from openeye import oechem


def SmartsAlign(refmol, fitmol, ss, ofs):
    unique = True
    for match1 in ss.Match(refmol, unique):
        for match2 in ss.Match(fitmol, unique):
            match = oechem.OEMatch()
            for mp1, mp2 in zip(match1.GetAtoms(), match2.GetAtoms()):
                match.AddPair(mp1.target, mp2.target)

            overlay = True
            rmat = oechem.OEDoubleArray(9)
            trans = oechem.OEDoubleArray(3)
            oechem.OERMSD(refmol, fitmol, match, overlay, rmat, trans)
            oechem.OERotate(fitmol, rmat)
            oechem.OETranslate(fitmol, trans)
            oechem.OEWriteConstMolecule(ofs, fitmol)


def main(argv=[__name__]):
    if len(argv) != 5:
        oechem.OEThrow.Usage("%s <refmol> <fitmol> <outfile> <smarts>" % argv[0])

    reffs = oechem.oemolistream()
    if not reffs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    if not oechem.OEIs3DFormat(reffs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input format: need 3D coordinates")
    refmol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(reffs, refmol):
        oechem.OEThrow.Fatal("Unable to read molecule in %s" % argv[1])
    if not refmol.GetDimension() == 3:
        oechem.OEThrow.Fatal("%s doesn't have 3D coordinates" % refmol.GetTitle())

    fitfs = oechem.oemolistream()
    if not fitfs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    if not oechem.OEIs3DFormat(fitfs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input format: need 3D coordinates")

    ofs = oechem.oemolostream()
    if not ofs.open(argv[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[3])
    if not oechem.OEIs3DFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid output format: need 3D coordinates")

    oechem.OEWriteConstMolecule(ofs, refmol)

    ss = oechem.OESubSearch()
    if not ss.Init(argv[4]):
        oechem.OEThrow.Fatal("Unable to parse SMARTS: %s" % argv[4])

    oechem.OEPrepareSearch(refmol, ss)
    if not ss.SingleMatch(refmol):
        oechem.OEThrow.Fatal("SMARTS fails to match refmol")

    for fitmol in fitfs.GetOEGraphMols():
        if not fitmol.GetDimension() == 3:
            oechem.OEThrow.Warning("%s doesn't have 3D coordinates" % fitmol.GetTitle())
            continue
        oechem.OEPrepareSearch(fitmol, ss)
        if not ss.SingleMatch(fitmol):
            oechem.OEThrow.Warning("SMARTS fails to match fitmol %s" % fitmol.GetTitle())
            continue
        SmartsAlign(refmol, fitmol, ss, ofs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
