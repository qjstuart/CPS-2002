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


def PrintLocations(mol, hideAtoms):
    """list alternate location codes and atom info (unless hideAtoms is True)"""
    if not oechem.OEHasResidues(mol):
        oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)

    alf = oechem.OEAltLocationFactory(mol)

    print("%s" % mol.GetTitle())

    print("grp-cnt=%d" % alf.GetGroupCount(), end=" ")
    if alf.GetGroupCount() > 0:
        print("{")
    else:
        print()

    for grp in alf.GetGroups():
        print(" grp=%d loc-cnt=%d grp-codes='%s'" %
              (grp.GetGroupID(), grp.GetLocationCount(), alf.GetLocationCodes(grp)))
        for loc in grp.GetLocations():
            print(" grp=%d loc=%d loc-codes='%s'" %
                  (loc.GetGroupID(), loc.GetLocationID(), alf.GetLocationCodes(loc)), end=" ")
            if not hideAtoms:
                print("[", end=" ")
            num_atoms = 0
            for atom in alf.GetAltAtoms(loc):
                num_atoms += 1
                if not hideAtoms:
                    res = oechem.OEAtomGetResidue(atom)
                    print("%s:%c:%s%d%c:c%cm%d;" %
                          (atom.GetName(), res.GetAlternateLocation(),
                           res.GetName(), res.GetResidueNumber(), res.GetInsertCode(),
                           res.GetChainID(), res.GetModelNumber()), end=" ")
            if not hideAtoms:
                print("]", end=" ")
            print(num_atoms)

    if alf.GetGroupCount() > 0:
        print("}")


def main(argv=[__name__]):
    if len(argv) != 2 and len(argv) != 3:
        oechem.OEThrow.Usage("%s [-H] <mol-infile>" % argv[0])

    hideAtoms = False
    filename = argv[1]
    if len(argv) == 3:
        if argv[1] != "-H":
            oechem.OEThrow.Fatal("Bad flag: %s (expecting -H)" % argv[1])
        hideAtoms = True
        filename = argv[2]

    ifs = oechem.oemolistream()
    if not ifs.open(filename):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % filename)

    # need this flavor to read alt loc atoms
    ifs.SetFlavor(oechem.OEFormat_PDB, oechem.OEIFlavor_PDB_ALTLOC)

    for mol in ifs.GetOEGraphMols():
        PrintLocations(mol, hideAtoms)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
