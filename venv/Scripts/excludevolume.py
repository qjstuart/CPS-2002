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

from __future__ import print_function
import os
import sys
from openeye import oechem
from openeye import oeshape


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    # Set up best overlay to the query molecule
    qfs = oechem.oemolistream()
    if not qfs.open(itf.GetString("-q")):
        oechem.OEThrow.Fatal("Unable to open %s" % itf.GetString("-q"))

    qmol = oechem.OEMol()
    oechem.OEReadMolecule(qfs, qmol)

    # Set up overlap to protein exclusion volume
    efs = oechem.oemolistream()
    if not efs.open(itf.GetString("-e")):
        oechem.OEThrow.Fatal("Unable to open %s" % itf.GetString("-e"))

    emol = oechem.OEMol()
    oechem.OEReadMolecule(efs, emol)

    evol = oeshape.OEExactShapeFunc()
    evol.SetupRef(emol)

    # open database and output streams
    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-d")):
        oechem.OEThrow.Fatal("Unable to open %s" % itf.GetString("-d"))

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s" % itf.GetString("-o"))

    print("Title                Combo  Rescore")
    for mol in ifs.GetOEMols():
        res = oeshape.OEROCSResult()
        oeshape.OEROCSOverlay(res, qmol, mol)
        outmol = res.GetOverlayConf()

        # calculate overlap with protein
        eres = oeshape.OEOverlapResults()
        evol.Overlap(outmol, eres)

        frac = eres.GetOverlap() / eres.GetFitSelfOverlap()
        rescore = res.GetTanimotoCombo() - frac

        # attach data to molecule and write it
        oechem.OESetSDData(outmol, "TanimotoCombo", "%-.3f" % res.GetTanimotoCombo())
        oechem.OESetSDData(outmol, "Exclusion Volume", "%-.3f" % eres.overlap)
        oechem.OESetSDData(outmol, "Fraction Overlap", "%-.3f" % frac)
        oechem.OESetSDData(outmol, "Rescore", "%-.3f" % rescore)

        oechem.OEWriteMolecule(ofs, outmol)

        print("%-20s %.3f  %.3f" %
              (outmol.GetTitle(), res.GetTanimotoCombo(), rescore))


#############################################################################
InterfaceData = """\
!CATEGORY %(prog)s
  !BRIEF %(prog)s [-q] <query> [-e] <exclusion> [-d] <database> [-o] <output>
  !PARAMETER -q 1
    !TYPE string
    !REQUIRED true
    !BRIEF Query file name
    !KEYLESS 1
  !END
  !PARAMETER -e 2
    !TYPE string
    !REQUIRED true
    !BRIEF Protein to use as exclusion volume
    !KEYLESS 2
  !END
  !PARAMETER -d 3
    !TYPE string
    !REQUIRED true
    !BRIEF Database file name
    !KEYLESS 3
  !END
  !PARAMETER -o 4
    !TYPE string
    !REQUIRED true
    !BRIEF Output file name
    !KEYLESS 4
  !END
!END
""" % {"prog": os.path.basename(sys.argv[0])}

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
