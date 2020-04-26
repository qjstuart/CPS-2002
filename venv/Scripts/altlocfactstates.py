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
import math
from openeye import oechem


def EnumerateStates(alf, locs, i, numGrps):
    """recursive function to print hex strings for all possible alt loc states
    alf     -- OEAltLocationFactory
    locs    -- list containing one location iterator per group
    i       -- index of current group
    numGrps -- total number of alternate location groups"""
    if i < numGrps:
        locs[i].ToFirst()
        for loc in locs[i]:
            alf.SetAlt(loc)
            EnumerateStates(alf, locs, i+1, numGrps)
    else:
        print(":".join([str(lit.Target().GetLocationID()) for lit in locs]), end=" ")
        state = alf.GetState()
        hstr = state.ToHexString()
        print("\t", hstr)


def PrintStates(mol):
    """list alternate location state information"""
    if not oechem.OEHasResidues(mol):
        oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)

    alf = oechem.OEAltLocationFactory(mol)

    print("%s\t%d groups" % (mol.GetTitle(), alf.GetGroupCount()), end=" ")

    tot = 1
    totexp = 0.0
    for grp in alf.GetGroups():
        tot *= grp.GetLocationCount()
        totexp += math.log10(grp.GetLocationCount())

    if totexp > 7.0:
        print("\tover 10^%.0f states" % totexp)
        print("too many states to enumerate")
    else:
        print("\t%d states" % tot)
        locs = [grp.GetLocations() for grp in alf.GetGroups()]
        EnumerateStates(alf, locs, 0, len(locs))


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <mol-infile>" % argv[0])

    ifs = oechem.oemolistream()

    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % argv[1])

    # need this flavor to read alt loc atoms
    ifs.SetFlavor(oechem.OEFormat_PDB, oechem.OEIFlavor_PDB_ALTLOC)

    for mol in ifs.GetOEGraphMols():
        PrintStates(mol)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
