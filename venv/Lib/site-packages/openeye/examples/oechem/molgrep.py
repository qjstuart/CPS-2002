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
# Perform substructure search on molecule file
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem


def SubSearch(itf, ss, ifs, ofs):
    reverseflag = itf.GetBool("-r")
    countflag = itf.GetBool("-c")
    count = 0
    for mol in ifs.GetOEGraphMols():
        oechem.OEPrepareSearch(mol, ss)
        if ss.SingleMatch(mol) != reverseflag:
            if countflag:
                count += 1
            else:
                oechem.OEWriteMolecule(ofs, mol)
    if countflag:
        print("%d matching molecules\n" % (count), end=" ")


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    if not (itf.GetBool("-c") ^ itf.HasString("-o")):
        oechem.OEThrow.Fatal("Counting (-c) or output (-o) must be \
                             specified and are mutually exclusive.")

    ifs = oechem.oemolistream()
    filename = itf.GetString("-i")
    if not ifs.open(filename):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % filename)

    ofs = oechem.oemolostream()
    if not itf.GetBool("-c"):
        filename = itf.GetString("-o")
        if not ofs.open(filename):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % filename)

    smarts = itf.GetString("-p")
    ss = oechem.OESubSearch()
    if not ss.Init(smarts):
        oechem.OEThrow.Fatal("Unable to parse SMARTS: %s" % smarts)

    SubSearch(itf, ss, ifs, ofs)


InterfaceData = """
!BRIEF  [-r][-c] -p smarts [-i] <input> [[-o] <output>]
!PARAMETER -i 1
  !ALIAS -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -p 2
  !TYPE string
  !REQUIRED true
  !BRIEF SMARTS pattern, quote for safety
!END
!PARAMETER -o 3
  !ALIAS -out
  !TYPE string
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -r 4
  !ALIAS -v
  !TYPE bool
  !DEFAULT false
  !BRIEF Reverse logic, not matched
!END
!PARAMETER -c 5
  !TYPE bool
  !DEFAULT false
  !BRIEF Just output count of number matched
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
