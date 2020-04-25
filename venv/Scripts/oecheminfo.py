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
# Print toolkit release date platform and build information. Also print out
# all formats supported by OEChem and whether they are readable or writeable
#############################################################################
from __future__ import print_function
import os
import sys
import openeye
from openeye import oechem


def GetYesNo(ok):
    if ok:
        return "yes"
    return "no"


def PrintFormats():
    print("code| ext           | description                       |read? |write?")
    print("----+---------------+-----------------------------------+------+------")
    for numformat in range(1, oechem.OEFormat_MAXFORMAT):
        extension = oechem.OEGetFormatExtension(numformat)
        description = oechem.OEGetFormatString(numformat)
        readable = GetYesNo(oechem.OEIsReadable(numformat))
        writeable = GetYesNo(oechem.OEIsWriteable(numformat))

        print(' %2d | %-13s | %-33s | %-4s | %-4s'
              % (numformat, extension, description, readable, writeable))
    print("----+---------------+-----------------------------------+------+------")


def ShowExamples():
    parent = os.path.abspath(os.path.dirname(openeye.__file__))
    print()
    print("Examples:", os.path.join(parent, 'examples'))
    print("Doc Examples:", os.path.join(parent, 'docexamples'))
    print()


def main(argv=sys.argv):
    print("Installed OEChem version: %s platform: %s built: %s release name: %s" %
          (oechem.OEChemGetRelease(), oechem.OEChemGetPlatform(),
           oechem.OEChemGetVersion(), oechem.OEToolkitsGetRelease()))
    ShowExamples()
    PrintFormats()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
