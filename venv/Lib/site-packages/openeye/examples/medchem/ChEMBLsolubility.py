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
# Utility to apply ChEMBL24 solubility transforms to an input set of structures
# ---------------------------------------------------------------------------
# ChEMBLsolubility.py [-i] input_mols [-o] output_mols
#                     [ -verbose ] [ -context [0|2] ] [ -minpairs # ]
#
# input_mols: filename of molecules to transform based on analysis
# output_mols: filename to collect transformed molecules
# [-verbose]: optional flag to request verbose progress
# [-context #]: optional flag to request a specific chemistry context
# [-minpairs #]: optional flag to request a minimum number of pairs to apply transforms
#############################################################################
from openeye import oechem
from openeye import oemedchem
import sys

############################################################
InterfaceData = """
!BRIEF [-i] <infile1> [-o] <infile2> [ -verbose ] [ -context [0|2]] [ -minpairs # ]
!PARAMETER -i
  !ALIAS -in
  !ALIAS -input
  !TYPE string
  !REQUIRED true
  !BRIEF Input file name
  !KEYLESS 1
!END
!PARAMETER -o
  !ALIAS -out
  !ALIAS -output
  !TYPE string
  !REQUIRED true
  !BRIEF Output file name
  !KEYLESS 2
!END
!PARAMETER -verbose
  !ALIAS -v
  !TYPE bool
  !DEFAULT false
  !BRIEF Verbose output
!END
!PARAMETER -context
  !ALIAS -c
  !TYPE string
  !DEFAULT 0
  !BRIEF Chemistry context for output
!END
!PARAMETER -minpairs 2
   !TYPE int
   !DEFAULT 0
   !BRIEF require at least -minpairs to apply the transformations (default: all)
!END
"""


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    verbose = itf.GetBool("-verbose")

    # input structure(s) to transform
    ifsmols = oechem.oemolistream()
    if not ifsmols.open(itf.GetString("-i")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-i"))

    # save output structure(s) to this file
    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-o")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-o"))

    # request a specific context for the transform activity, here 0-bonds
    chemctxt = oemedchem.OEMatchedPairContext_Bond0
    askcontext = itf.GetString("-context")[:1]
    if askcontext == '0':
        chemctxt = oemedchem.OEMatchedPairContext_Bond0
    elif askcontext == '2':
        chemctxt = oemedchem.OEMatchedPairContext_Bond2
    else:
        oechem.OEThrow.Fatal("Invalid context specified: " +
                             askcontext + ", only 0|2 allowed")

    minpairs = itf.GetInt("-minpairs")
    if minpairs > 1 and verbose:
        print('Requiring at least {0:d} matched pairs to apply transformations'.format(minpairs))

    irec = 0
    ocnt = 0
    ototal = 0
    for mol in ifsmols.GetOEGraphMols():
        irec += 1
        oechem.OEDeleteEverythingExceptTheFirstLargestComponent(mol)
        iter = oemedchem.OEApplyChEMBL24SolubilityTransforms(mol, chemctxt, minpairs)
        if not iter.IsValid():
            name = mol.GetTitle()
            if not mol.GetTitle():
                name = 'record ' + str(irec)
            oechem.OEThrow.Warning("%s: did not produce any output" % name)
            continue
        ocnt = 0
        for outmol in iter:
            ocnt += 1
            oechem.OEWriteMolecule(ofs, outmol)
        if not ocnt:
            print('Record', irec, 'No output generated')
            print(oechem.OEMolToSmiles(mol))
        else:
            ototal += ocnt
            if verbose:
                print('Record:', "{0:4d}".format(irec),
                      'transformation count=', "{0:6d}".format(ocnt),
                      'total mols=', "{0:7d}".format(ototal))

    if not irec:
        oechem.OEThrow.Fatal('No records in input structure file to transform')

    if not ocnt:
        oechem.OEThrow.Warning('No transformed structures generated')

    print("Input molecules={0:d} output molecules={1:d}".format(irec, ototal))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
