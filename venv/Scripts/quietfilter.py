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
#  Quietly filter a molecule file
#############################################################################
import sys
from openeye import oechem
from openeye import oemolprop


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    oemolprop.OEConfigureFilterParams(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    iname = itf.GetString("-in")
    oname = itf.GetString("-out")

    ifs = oechem.oemolistream()
    if not ifs.open(iname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    ofs = oechem.oemolostream()
    if not ofs.open(oname):
        oechem.OEThrow.Fatal("Cannot create output file!")

    ftype = oemolprop.OEGetFilterType(itf)
    filt = oemolprop.OEFilter(ftype)

    ver = itf.GetInt("-verbose")
    oechem.OEThrow.SetLevel(ver)

    for mol in ifs.GetOEGraphMols():
        if filt(mol):
            oechem.OEWriteMolecule(ofs, mol)


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF [-in] <input> [-out] <output> [-verbose] <verbose>

!CATEGORY "input/output options :"

    !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !REQUIRED true
      !KEYLESS 1
      !VISIBILITY simple
      !BRIEF Input filename
    !END

    !PARAMETER -out
      !ALIAS -o
      !TYPE string
      !REQUIRED true
      !KEYLESS 2
      !VISIBILITY simple
      !BRIEF Output filename
    !END

!END

!CATEGORY "other options :"

    !PARAMETER -verbose
    !TYPE int
    !REQUIRED false
    !LEGAL_RANGE 2 5
    !DEFAULT 4
    !VISIBILITY simple
    !BRIEF Error level of messages
    !DETAIL
        2 is Verbose
        3 is Info
        4 is Warning
        5 is Error
  !END

!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
