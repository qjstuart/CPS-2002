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
# Extract the number of Lipinski violations from the table output
#############################################################################
from __future__ import print_function
import sys
from openeye import oechem
from openeye import oemolprop


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    oemolprop.OEConfigureFilterParams(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    iname = itf.GetString("-in")

    ifs = oechem.oemolistream()
    if not ifs.open(iname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    ftype = oemolprop.OEGetFilterType(itf)
    filt = oemolprop.OEFilter(ftype)

    ver = itf.GetInt("-verbose")
    oechem.OEThrow.SetLevel(ver)

    ostr = oechem.oeosstream()
    pwnd = False
    filt.SetTable(ostr, pwnd)

    headers = ostr.str().split(b'\t')
    ostr.clear()  # remove the header row from the stream

    for mol in ifs.GetOEGraphMols():
        filt(mol)

        fields = ostr.str().decode("UTF-8").split('\t')
        ostr.clear()  # remove this row from the stream

        tmpdct = dict(zip(headers, fields))
        print(mol.GetTitle(), tmpdct[b"Lipinski violations"])


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF [-in] <input> [-verbose] <verbose>

!CATEGORY "input/output options :"

    !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !REQUIRED true
      !KEYLESS 1
      !VISIBILITY simple
      !BRIEF Input filename
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
