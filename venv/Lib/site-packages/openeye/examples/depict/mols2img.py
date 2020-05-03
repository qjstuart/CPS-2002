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
# Converts molecules into an image with grid layout.
# The output file format depends on its file extension.
#############################################################################

import sys
from openeye import oechem
from openeye import oedepict


def main(argv=[__name__]):

    itf = oechem.OEInterface()
    oechem.OEConfigure(itf, InterfaceData)
    oedepict.OEConfigureImageWidth(itf, 400.0)
    oedepict.OEConfigureImageHeight(itf, 400.0)
    oedepict.OEConfigureImageGridParams(itf)
    oedepict.OEConfigurePrepareDepictionOptions(itf)
    oedepict.OEConfigure2DMolDisplayOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    oname = itf.GetString("-out")

    ext = oechem.OEGetFileExtension(oname)
    if not oedepict.OEIsRegisteredImageFile(ext):
        oechem.OEThrow.Fatal("Unknown image type!")

    ofs = oechem.oeofstream()
    if not ofs.open(oname):
        oechem.OEThrow.Fatal("Cannot open output file!")

    width, height = oedepict.OEGetImageWidth(itf), oedepict.OEGetImageHeight(itf)
    image = oedepict.OEImage(width, height)

    rows = oedepict.OEGetImageGridNumRows(itf)
    cols = oedepict.OEGetImageGridNumColumns(itf)
    grid = oedepict.OEImageGrid(image, rows, cols)

    popts = oedepict.OEPrepareDepictionOptions()
    oedepict.OESetupPrepareDepictionOptions(popts, itf)

    dopts = oedepict.OE2DMolDisplayOptions()
    oedepict.OESetup2DMolDisplayOptions(dopts, itf)
    dopts.SetDimensions(grid.GetCellWidth(), grid.GetCellHeight(), oedepict.OEScale_AutoScale)

    celliter = grid.GetCells()
    for iname in itf.GetStringList("-in"):
        ifs = oechem.oemolistream()
        if not ifs.open(iname):
            oechem.OEThrow.Warning("Cannot open %s input file!" % iname)
            continue

        for mol in ifs.GetOEGraphMols():
            if not celliter.IsValid():
                break

            oedepict.OEPrepareDepiction(mol, popts)
            disp = oedepict.OE2DMolDisplay(mol, dopts)
            oedepict.OERenderMolecule(celliter.Target(), disp)
            celliter.Next()

    oedepict.OEWriteImage(ofs, ext, image)

    return 0


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF -in <input1> [ <input2> .. ] -out <output image>

!CATEGORY "input/output options :"

    !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !LIST true
      !REQUIRED true
      !VISIBILITY simple
      !BRIEF Input filename(s)
    !END

    !PARAMETER -out
      !ALIAS -o
      !TYPE string
      !REQUIRED true
      !VISIBILITY simple
      !BRIEF Output filename
    !END

!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
