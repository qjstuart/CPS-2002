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
# Utility to fragment the input structures by Bemis-Murcko rules
# ---------------------------------------------------------------------------
# BemisMurckoPerception.py [ -uncolor ] [-i] <input_mols> [-o] <output_mols>
#
# input_mols: filename of molecules to fragment and uncolor
# output_mols: filename of output structures annotated with SD data of perceived regions
# [ -uncolor ]: optional arg to request uncoloring of output fragment info
#############################################################################
from openeye import oechem
from openeye import oemedchem
import sys

############################################################
InterfaceData = """
!BRIEF [ -uncolor ] [-i] <infile1> [-o] <infile2>
!PARAMETER -i
  !ALIAS -in
  !ALIAS -input
  !TYPE string
  !REQUIRED true
  !BRIEF Input structure file name
  !KEYLESS 1
!END
!PARAMETER -o
  !ALIAS -out
  !ALIAS -output
  !TYPE string
  !REQUIRED true
  !BRIEF Output SD file name
  !KEYLESS 2
!END
!PARAMETER -uncolor
  !ALIAS -u
  !TYPE bool
  !DEFAULT false
  !BRIEF Uncolor output molecules
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    # flag on command line indicates uncoloring option or not
    bUncolor = itf.GetBool("-uncolor")

    # input structure(s) to transform
    ifsmols = oechem.oemolistream()
    if not ifsmols.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    # save output structure(s) to this file
    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))
    if not oechem.OEIsSDDataFormat(ofs.GetFormat()):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    irec = 0
    ototal = 0
    frag = oechem.OEGraphMol()
    for mol in ifsmols.GetOEGraphMols():
        irec += 1
        oechem.OEDeleteEverythingExceptTheFirstLargestComponent(mol)
        iter = oemedchem.OEGetBemisMurcko(mol)
        if not iter.IsValid():
            name = mol.GetTitle()
            if not mol.GetTitle():
                name = 'Record ' + str(irec)
            oechem.OEThrow.Warning("%s: no perceived regions" % name)
            continue
        for bmregion in iter:
            # create a fragment from the perceived region
            oechem.OESubsetMol(frag, mol, bmregion, True)
            if bUncolor:
                # ignore 3D stereo parities
                if (frag.GetDimension() == 3):
                    frag.SetDimension(0)
                # uncolor the fragment
                oechem.OEUncolorMol(frag)
            smi = oechem.OEMolToSmiles(frag)
            # annotate the input molecule with the role information
            for role in bmregion.GetRoles():
                oechem.OEAddSDData(mol, role.GetName(), smi)
        ototal += 1
        oechem.OEWriteMolecule(ofs, mol)

    if not irec:
        oechem.OEThrow.Fatal('No records in input structure file to perceive')

    if not ototal:
        oechem.OEThrow.Warning('No annotated structures generated')

    print("Input molecules={0:d}, output annotated {1:s}molecules={2:d}"
          .format(irec, ("(uncolored) " if bUncolor else ""), ototal))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
