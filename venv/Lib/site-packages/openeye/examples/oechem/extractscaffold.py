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
# Extract the ring scaffold of a molecule
#############################################################################
from openeye import oechem
try:
    set()
except NameError:
    from sets import Set as set
import sys


def TraverseForRing(visited, atom):
    visited.add(atom.GetIdx())

    for nbor in atom.GetAtoms():
        if nbor.GetIdx() not in visited:
            if nbor.IsInRing():
                return True

            if TraverseForRing(visited, nbor):
                return True

    return False


def DepthFirstSearchForRing(root, nbor):
    visited = set()
    visited.add(root.GetIdx())

    return TraverseForRing(visited, nbor)


class IsInScaffold(oechem.OEUnaryAtomPred):
    def __call__(self, atom):
        if atom.IsInRing():
            return True

        count = 0
        for nbor in atom.GetAtoms():
            if DepthFirstSearchForRing(atom, nbor):
                count += 1

        return count > 1


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    exo_dbl_bonds = itf.GetBool("-exo")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    for src in ifs.GetOEMols():
        dst = oechem.OEMol()
        pred = IsInScaffold()
        if exo_dbl_bonds:
            pred = oechem.OEOrAtom(pred, oechem.OEIsNonRingAtomDoubleBondedToRing())

        adjustHcount = True
        oechem.OESubsetMol(dst, src, pred, adjustHcount)

        if dst.IsValid():
            oechem.OEWriteMolecule(ofs, dst)


InterfaceData = """
!BRIEF [-exo] [-i] <input> [-o] <scaffolds>
!PARAMETER -i
  !ALIAS -in
  !TYPE string
  !REQUIRED true
  !BRIEF input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !ALIAS -out
  !TYPE string
  !REQUIRED true
  !BRIEF output file name
  !KEYLESS 2
!END
!PARAMETER -exo
  !TYPE bool
  !DEFAULT true
  !BRIEF Exclude double bonds exo to ring in scaffold
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
