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
import sys
from openeye import oechem


def PrintGroups(mol):
    """summarize alternate location group info"""
    if not oechem.OEHasResidues(mol):
        oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)

    alf = oechem.OEAltLocationFactory(mol)

    print("%s\t(%s groups)" %
          (mol.GetTitle(), alf.GetGroupCount()))

    for grp in alf.GetGroups():
        print("\t%s locs:%s" %
              (grp.GetLocationCount(), alf.GetLocationCodes(grp)))


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <mol-infile>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])

    # need this flavor to read alt loc atoms
    ifs.SetFlavor(oechem.OEFormat_PDB, oechem.OEIFlavor_PDB_ALTLOC)

    for mol in ifs.GetOEGraphMols():
        PrintGroups(mol)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
