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
# Extract properties from SD file and save as CSV
#############################################################################
import sys
from openeye import oechem


def SDF2CSV(ifs, csv):
    taglist = []
    # read through once to find all unique tags
    for mol in ifs.GetOEGraphMols():
        for dp in oechem.OEGetSDDataPairs(mol):
            if dp.GetTag() not in taglist:
                taglist.append(dp.GetTag())

    ifs.rewind()
    # print out column labels
    header = "Title"
    for tag in taglist:
        header += ",%s" % tag
    header += '\n'
    csv.write(header)

    # build csv file
    for mol in ifs.GetOEGraphMols():
        line = [mol.GetTitle()]
        for tag in taglist:
            if oechem.OEHasSDData(mol, tag):
                value = oechem.OEGetSDData(mol, tag)
            else:
                value = ''
            line.append(',')
            line.append(value)
        csv.write(''.join(line))
        csv.write('\n')


def main(argv=[__name__]):
    if len(argv) != 3:
        oechem.OEThrow.Usage("%s <infile> <csvfile>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])
    if ifs.GetFormat() not in [oechem.OEFormat_SDF, oechem.OEFormat_OEB]:
        oechem.OEThrow.Fatal("Only works for sdf or oeb input files")

    csv = oechem.oeofstream()
    if not csv.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % argv[2])

    SDF2CSV(ifs, csv)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
