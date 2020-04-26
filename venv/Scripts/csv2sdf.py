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
# Merge a CSV file of data/properties, key on compound name in first column
# and use column titles as keys.  All data is read/written as strings
#############################################################################
import sys
import csv
from openeye import oechem


def CSV2SDF(csvfile, ifs, ofs):
    reader = csv.reader(csvfile, delimiter=',')
    propnames = next(reader)
    values = {}
    for row in reader:
        title = row[0]
        if title == "":
            oechem.OEThrow.Warning("Skipping entry with no title")
            continue
        value = row[1:]
        values[title] = value

    for mol in ifs.GetOEGraphMols():
        if mol.GetTitle() in values:
            count = 0
            for v in values[mol.GetTitle()]:
                count += 1
                if v == "":
                    continue
                else:
                    oechem.OESetSDData(mol, propnames[count], v)
        oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <csvfile> <infile> <outsdfile>" % argv[0])
    try:
        csvfile = open(argv[1])
    except Exception:
        oechem.OEThrow.Fatal("Unable to open %s csv for reading" % argv[1])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[2])

    ofs = oechem.oemolostream()
    if not ofs.open(argv[3]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[3])

    if ofs.GetFormat() not in [oechem.OEFormat_SDF, oechem.OEFormat_OEB]:
        oechem.OEThrow.Fatal("Only works for sdf or oeb output files")

    CSV2SDF(csvfile, ifs, ofs)

    csvfile.close()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
