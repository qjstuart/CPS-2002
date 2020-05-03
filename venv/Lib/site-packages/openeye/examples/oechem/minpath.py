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
# Find the minimum path length between 2 smarts patterns
# or the path length between 2 named atoms
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def AtomPathLength(ifs, ofs, itf, atm1, atm2):
    for mol in ifs.GetOEGraphMols():
        oechem.OETriposAtomNames(mol)

        a1 = None
        a2 = None
        for atm in mol.GetAtoms():
            if atm.GetName() == atm1:
                a1 = atm
            if atm.GetName() == atm2:
                a2 = atm
            if a1 is not None and a2 is not None:
                break

        if a1 is None or a2 is None:
            oechem.OEThrow.Warning("Failed to find atoms %s and %s in molecule" % (atm1, atm2))
            continue

        pathlen = oechem.OEGetPathLength(a1, a2)
        if itf.GetBool("-verbose") or not itf.HasString("-o"):
            print("Path length: %s in %s" % (pathlen, oechem.OEMolToSmiles(mol)))

        spath = oechem.OEShortestPath(a1, a2)
        spathmol = oechem.OEGraphMol()
        adjustHCount = True
        oechem.OESubsetMol(spathmol, mol, oechem.OEIsAtomMember(spath), adjustHCount)
        spathsmiles = oechem.OEMolToSmiles(spathmol)

        if itf.HasString("-o"):
            oechem.OEWriteMolecule(ofs, spathmol)
        elif itf.GetBool("-verbose"):
            print(spathsmiles)


def SmartsPathLength(ifs, ofs, itf, ss1, ss2):
    for mol in ifs.GetOEGraphMols():
        oechem.OEPrepareSearch(mol, ss1)
        oechem.OEPrepareSearch(mol, ss2)
        if not (ss1.SingleMatch(mol) and ss2.SingleMatch(mol)):
            oechem.OEThrow.Warning("Unable to find SMARTS matches in %s, skipping" % mol.GetTitle())
            continue

        unique = True
        allminlen = sys.maxsize
        for match1 in ss1.Match(mol, unique):
            for match2 in ss2.Match(mol, unique):
                minlen = sys.maxsize
                for atom1 in match1.GetTargetAtoms():
                    for atom2 in match2.GetTargetAtoms():
                        pathlen = oechem.OEGetPathLength(atom1, atom2)
                        if minlen > pathlen:
                            minlen = pathlen
                            atompairs = []
                            atompairs.append([atom1, atom2])

                        elif minlen == pathlen:
                            atompairs.append([atom1, atom2])

                if minlen < allminlen:
                    allminlen = minlen
                    allatompairs = atompairs[:]

                elif minlen == allminlen:
                    allatompairs += atompairs[:]

        if itf.GetBool("-verbose") or not itf.HasString("-o"):
            print("Shortest path length: %s in %s" % (allminlen, oechem.OEMolToSmiles(mol)))

        spathlist = set()
        for satom1, satom2, in allatompairs:
            spath = oechem.OEShortestPath(satom1, satom2)
            spathmol = oechem.OEGraphMol()
            oechem.OESubsetMol(spathmol, mol, oechem.OEIsAtomMember(spath))
            spathsmiles = oechem.OEMolToSmiles(spathmol)

            if spathsmiles in spathlist:
                continue
            spathlist.add(spathsmiles)

            if itf.HasString("-o"):
                oechem.OEWriteMolecule(ofs, spathmol)
            elif itf.GetBool("-verbose"):
                print(spathsmiles)

    return


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)

    if not ((itf.HasString("-smarts1") and itf.HasString("-smarts2")) ^
            (itf.HasString("-atom1") and itf.HasString("-atom2"))):
        oechem.OEThrow.Fatal("-smarts1 and -smarts2 or -atom1 and -atom2 must be set")

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" %
                             itf.GetString("-i").rstrip())

    ofs = oechem.oemolostream()
    if itf.HasString("-o"):
        if not ofs.open(itf.GetString("-o")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    if itf.HasString("-smarts1") and itf.HasString("-smarts2"):
        ss1 = oechem.OESubSearch()
        smarts1 = itf.GetString("-smarts1")
        if not ss1.Init(smarts1):
            oechem.OEThrow.Fatal("Unable to parse SMARTS1: %s" % smarts1.rstrip())

        ss2 = oechem.OESubSearch()
        smarts2 = itf.GetString("-smarts2")
        if not ss2.Init(smarts2):
            oechem.OEThrow.Fatal("Unable to parse SMARTS2: %s" % smarts2.rstrip())

        SmartsPathLength(ifs, ofs, itf, ss1, ss2)

    else:
        atom1 = itf.GetString("-atom1")
        atom2 = itf.GetString("-atom2")
        AtomPathLength(ifs, ofs, itf, atom1, atom2)


Interface = """
!BRIEF -i <input> [-o <output>] -smarts1 <smarts> -smarts2 <smarts> | -atom1 <name> -atom2 <name>
!PARAMETER -i
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !TYPE string
  !REQUIRED false
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -smarts1
  !TYPE string
  !BRIEF Smarts pattern to identify 1st atom
!END
!PARAMETER -smarts2
  !TYPE string
  !BRIEF Smarts pattern to identify 2nd atom
!END
!PARAMETER -atom1
  !TYPE string
  !BRIEF Name of 1st atom
!END
!PARAMETER -atom2
  !TYPE string
  !BRIEF Name of 2nd atom
!END
!PARAMETER -verbose
  !TYPE bool
  !REQUIRED false
  !DEFAULT false
  !BRIEF Print verbose output
!END
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
