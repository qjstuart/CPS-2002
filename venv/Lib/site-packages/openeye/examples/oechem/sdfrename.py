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
# Rename SDF molecules by specified field
#############################################################################
import sys
from openeye import oechem


def Rename(ifs, ofs, fieldname):
    for mol in ifs.GetOEGraphMols():
        if oechem.OEHasSDData(mol, fieldname):
            mol.SetTitle(oechem.OEGetSDData(mol, fieldname))
        else:
            title = mol.GetTitle()
            oechem.OEThrow.Warning("Renaming of molecule %s failed; no field %s" %
                                   (title, fieldname))
        oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <fieldname> <infile> <outfile>" % argv[0])

    fieldname = argv[1]
    ifs = oechem.oemolistream()
    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])
    if not oechem.OEIsSDDataFormat(ifs.GetFormat()):
        oechem.OEThrow.Fatal("Only works for input file formats that support SD data (sdf,oeb,csv)")

    ofs = oechem.oemolostream()
    if not ofs.open(argv[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[3])

    Rename(ifs, ofs, fieldname)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
