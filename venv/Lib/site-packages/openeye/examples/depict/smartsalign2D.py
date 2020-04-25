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
# Aligns molecules to a smarts pattern
#############################################################################

import sys
from openeye import oechem
from openeye import oedepict


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    iname = itf.GetString("-in")
    oname = itf.GetString("-out")
    smarts = itf.GetString("-smarts")

    qmol = oechem.OEQMol()
    if not oechem.OEParseSmarts(qmol, smarts):
        oechem.OEThrow.Fatal("Invalid SMARTS: %s" % smarts)
    oechem.OEGenerate2DCoordinates(qmol)

    ss = oechem.OESubSearch(qmol)
    if not ss.IsValid():
        oechem.OEThrow.Fatal("Unable to initialize substructure search!")

    ifs = oechem.oemolistream()
    if not ifs.open(iname):
        oechem.OEThrow.Fatal("Cannot open input molecule file!")

    ofs = oechem.oemolostream()
    if not ofs.open(oname):
        oechem.OEThrow.Fatal("Cannot open output file!")
    if not oechem.OEIs2DFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Invalid output format for 2D coordinates")

    for mol in ifs.GetOEGraphMols():
        oechem.OEPrepareSearch(mol, ss)

        alignres = oedepict.OEPrepareAlignedDepiction(mol, ss)
        if not alignres.IsValid():
            oechem.OEThrow.Warning("Substructure is not found in input molecule!")
            oedepict.OEPrepareDepiction(mol)

        oechem.OEWriteMolecule(ofs, mol)

    return 0


#############################################################################
# INTERFACE
#############################################################################

InterfaceData = '''
!BRIEF [-in] <input> [-smarts] <smarts> [-out] <output>

!CATEGORY "input/output options :"

    !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !REQUIRED true
      !KEYLESS 1
      !VISIBILITY simple
      !BRIEF Filename of input molecules
    !END

    !PARAMETER -smarts
      !ALIAS -s
      !TYPE string
      !REQUIRED true
      !KEYLESS 2
      !VISIBILITY simple
      !BRIEF SMARTS for alignment match
    !END

    !PARAMETER -out
      !ALIAS -o
      !TYPE string
      !REQUIRED true
      !KEYLESS 3
      !VISIBILITY simple
      !BRIEF Output filename
    !END

!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
