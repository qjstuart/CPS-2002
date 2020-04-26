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


def DropLigandFromProtein(prot, lig):
    """delete atoms from the protein w/same coords as the ligand
    as well as any waters"""

    approximatelyTheSame = 0.05
    nn = oechem.OENearestNbrs(prot, approximatelyTheSame)

    # mark ligand atoms for deletion
    bv = oechem.OEBitVector(prot.GetMaxAtomIdx())
    for nbrs in nn.GetNbrs(lig):
        r1 = oechem.OEAtomGetResidue(nbrs.GetBgn())
        r2 = oechem.OEAtomGetResidue(nbrs.GetEnd())
        if r1.GetModelNumber() == r2.GetModelNumber():
            bv.SetBitOn(nbrs.GetBgn().GetIdx())

    # mark waters for deletion too
    for atom in prot.GetAtoms():
        res = oechem.OEAtomGetResidue(atom)
        if oechem.OEGetResidueIndex(res) == oechem.OEResidueIndex_HOH:
            bv.SetBitOn(atom.GetIdx())

    pred = oechem.OEAtomIdxSelected(bv)
    for atom in prot.GetAtoms(pred):
        prot.DeleteAtom(atom)


def LigandProteinCloseContacts(prot, lig, maxgap):
    """atoms in the protein within maxgap Angstroms of the ligand"""

    oechem.OESuppressHydrogens(prot)
    oechem.OESuppressHydrogens(lig)

    DropLigandFromProtein(prot, lig)

    nn = oechem.OENearestNbrs(prot, maxgap)

    return list(nn.GetNbrs(lig))


def PrintCloseContacts(prot, lig, maxgap):
    """print atoms in the protein within maxgap Angstroms of the ligand"""

    contacts = LigandProteinCloseContacts(prot, lig, maxgap)

    if len(contacts) > 0:
        print("%s: %d contacts within %.2fA" % (prot.GetTitle(), len(contacts), maxgap))
        for nbrs in contacts:
            pat = nbrs.GetBgn()
            lat = nbrs.GetEnd()
            rp = oechem.OEAtomGetResidue(pat)
            rl = oechem.OEAtomGetResidue(lat)
            print("%6.2fA:%5s %4s%s %s %s %4s%s:%5s %4s%s %s %s %4s%s" %
                  (math.sqrt(nbrs.GetDist2()),
                   rp.GetSerialNumber(), pat.GetName(), rp.GetAlternateLocation(),
                   rp.GetName(), rp.GetChainID(), rp.GetResidueNumber(), rp.GetInsertCode(),
                   rl.GetSerialNumber(), lat.GetName(), rl.GetAlternateLocation(),
                   rl.GetName(), rl.GetChainID(), rl.GetResidueNumber(), rl.GetInsertCode()))
        print()


def main(argv=[__name__]):
    if len(argv) != 4:
        oechem.OEThrow.Usage("%s <prot-infile> <lig-infile> <max-distance>" % argv[0])

    ifs = oechem.oemolistream()
    if not ifs.open(argv[1]):
        oechem.OEThrow.Fatal("Unable to open protein %s for reading" % argv[1])

    prot = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, prot)
    if not oechem.OEHasResidues(prot):
        oechem.OEPerceiveResidues(prot, oechem.OEPreserveResInfo_All)

    ifs = oechem.oemolistream()
    if not ifs.open(argv[2]):
        oechem.OEThrow.Fatal("Unable to open ligand %s for reading" % argv[2])

    lig = oechem.OEGraphMol()
    oechem.OEReadMolecule(ifs, lig)
    if not oechem.OEHasResidues(lig):
        oechem.OEPerceiveResidues(lig, oechem.OEPreserveResInfo_All)

    maxgap = float(argv[3])

    PrintCloseContacts(prot, lig, maxgap)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
