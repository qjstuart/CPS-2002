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
# Converts an MDL query structure into an image file.
# The output file format depends on its file extension.
#############################################################################

import sys
from openeye import oechem
from openeye import oedepict


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData)
    oedepict.OEConfigureImageOptions(itf)
    oedepict.OEConfigure2DMolDisplayOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    iname = itf.GetString("-in")
    oname = itf.GetString("-out")

    ext = oechem.OEGetFileExtension(oname)
    if not oedepict.OEIsRegisteredImageFile(ext):
        oechem.OEThrow.Fatal("Unknown image type!")

    ifs = oechem.oemolistream()
    if not ifs.open(iname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    if ifs.GetFormat() != oechem.OEFormat_MDL:
        oechem.OEThrow.Fatal("Input file is not an MDL query file")

    ofs = oechem.oeofstream()
    if not ofs.open(oname):
        oechem.OEThrow.Fatal("Cannot open output file!")

    mol = oechem.OEGraphMol()
    if not oechem.OEReadMDLQueryFile(ifs, mol):
        oechem.OEThrow.Fatal("Cannot read mdl query input file!")

    clearcoords, suppressH = False, False
    oedepict.OEPrepareDepiction(mol, clearcoords, suppressH)

    width, height = oedepict.OEGetImageWidth(itf), oedepict.OEGetImageHeight(itf)
    opts = oedepict.OE2DMolDisplayOptions(width, height, oedepict.OEScale_AutoScale)
    oedepict.OESetup2DMolDisplayOptions(opts, itf)

    disp = oedepict.OE2DMolDisplay(mol, opts)
    oedepict.OERenderMolecule(ofs, ext, disp)

    return 0


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF [-in] <input> [-out] <output image>

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
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
