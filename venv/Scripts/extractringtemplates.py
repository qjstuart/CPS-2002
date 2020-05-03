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
# Extracts ring templates for 2D coordinate generation
#############################################################################

import sys
from openeye import oechem


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData, argv)

    ifname = itf.GetString("-in")
    ofname = itf.GetString("-out")

    ifs = oechem.oemolistream()
    if not ifs.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifname)

    if not oechem.OEIs2DFormat(ifs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input format: need 2D coordinates")

    ofs = oechem.oemolostream()
    if not ofs.open(ofname):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % ofname)

    if not oechem.OEIs2DFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid output format: unable to write 2D coordinates")

    nrrings = 0
    for mol in ifs.GetOEGraphMols():
        for ring in oechem.OEExtractRingTemplates(mol):
            nrrings += 1
            oechem.OEWriteMolecule(ofs, ring)

    oechem.OEThrow.Info("%d number of ring templates extracted" % nrrings)


InterfaceData = """
!BRIEF [-i] <input> [-o] <output>
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
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
