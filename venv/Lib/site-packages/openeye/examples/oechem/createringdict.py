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
# Creates a new 2D ring dictionary
#############################################################################

import sys
from openeye import oechem


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData, argv)

    ifname = itf.GetString("-in")
    ofname = itf.GetString("-ringdict")

    ifs = oechem.oemolistream()
    if not ifs.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading!" % ifname)

    if not oechem.OEIs2DFormat(ifs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid input file format for 2D coordinates!")

    ofs = oechem.oemolostream()
    if not ofs.open(ofname):
        oechem.OEThrow.Fatal("Unable to open %s for writing!" % ofname)

    if ofs.GetFormat() != oechem.OEFormat_OEB:
        oechem.OEThrow.Fatal("Output file has to be OEB format!")

    opts = oechem.OE2DRingDictionaryCreatorOptions()
    opts.SetRetainExistingBuiltInTemplates(itf.GetBool('-retain-built-in'))

    ringdict = oechem.OE2DRingDictionary(opts)

    dots = oechem.OEDots(10000, 100, "molecules")

    for mol in ifs.GetOEGraphMols():
        dots.Update()
        ringdict.AddRings(mol)

    nrrings = ringdict.NumRings()
    oechem.OEThrow.Info("%d ring template(s) have been extracted!" % nrrings)

    if nrrings != 0:
        oechem.OEWrite2DRingDictionary(ofname, ringdict)

    return 0


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = """
!BRIEF [-in] <input> [-ringdict] <output ringdict>

!CATEGORY "input/output options :"

  !PARAMETER -in
    !ALIAS -i
    !TYPE string
    !REQUIRED true
    !KEYLESS 1
    !VISIBILITY simple
    !BRIEF Input 2D molecule filename
  !END

  !PARAMETER -ringdict
    !ALIAS -rd
    !TYPE string
    !REQUIRED true
    !KEYLESS 2
    !VISIBILITY simple
    !BRIEF Output ring dictionary OEB filename
  !END

!END

!CATEGORY "ring dictionary options :"

  !PARAMETER -retain-built-in
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF Ignore ring template if built-in exists
  !END

!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
