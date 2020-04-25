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
# Perform library generation with SMIRKS
#############################################################################
import sys
from openeye import oechem


def LibGen(libgen, ofs, unique, isomeric):
    smiflag = oechem.OESMILESFlag_DEFAULT  # Canonical|AtomMaps|Rgroup
    if isomeric:
        smiflag |= oechem.OESMILESFlag_ISOMERIC
    # access products
    uniqproducts = []
    for mol in libgen.GetProducts():
        smiles = oechem.OECreateSmiString(mol, smiflag)
        if not unique or smiles not in uniqproducts:
            uniqproducts.append(smiles)
            oechem.OEWriteMolecule(ofs, mol)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    if not itf.HasString("-smirks") and not itf.HasString("-rxn"):
        oechem.OEThrow.Fatal("Please provide SMIRKS string or MDL reaction file")

    if itf.HasString("-smirks") and itf.HasString("-rxn"):
        oechem.OEThrow.Fatal("Please provide only SMIRKS string or MDL reaction file")

    reaction = oechem.OEQMol()
    if itf.HasString("-smirks"):
        smirks = itf.GetString("-smirks")
        if not oechem.OEParseSmirks(reaction, smirks):
            oechem.OEThrow.Fatal("Unable to parse SMIRKS: %s" % smirks)
    else:
        rxn = itf.GetString("-rxn")
        rfile = oechem.oemolistream(rxn)
        opt = oechem.OEMDLQueryOpts_ReactionQuery | oechem.OEMDLQueryOpts_SuppressExplicitH
        if not oechem.OEReadMDLReactionQueryFile(rfile, reaction, opt):
            oechem.OEThrow.Fatal("Unable to read reaction file: %s" % rxn)

    relax = itf.GetBool("-relax")
    unique = itf.GetBool("-unique")
    implicitH = itf.GetBool("-implicitH")
    valcorrect = itf.GetBool("-valence")
    isomeric = itf.GetBool("-isomeric")

    libgen = oechem.OELibraryGen()
    if not libgen.Init(reaction, not relax):
        oechem.OEThrow.Fatal("failed to initialize library generator")
    libgen.SetValenceCorrection(valcorrect)
    libgen.SetExplicitHydrogens(not implicitH)
    libgen.SetClearCoordinates(True)

    ofs = oechem.oemolostream(".smi")
    if itf.HasString("-product"):
        ofs.open(itf.GetString("-product"))

    nrReacts = 0
    while itf.HasString("-reactants", nrReacts):
        fileName = itf.GetString("-reactants", nrReacts)
        if nrReacts >= libgen.NumReactants():
            oechem.OEThrow.Fatal("Number of reactant files exceeds number of \
                                 reactants specified in reaction")
        ifs = oechem.oemolistream()
        if not ifs.open(fileName):
            oechem.OEThrow.Fatal("Unable to read %s reactant file" % fileName)
        for mol in ifs.GetOEGraphMols():
            libgen.AddStartingMaterial(mol, nrReacts, unique)
        nrReacts += 1

    if nrReacts != libgen.NumReactants():
        oechem.OEThrow.Fatal("Reactions requires %d reactant files!" % libgen.NumReactants())
    LibGen(libgen, ofs, unique, isomeric)


InterfaceData = """
!BRIEF [options] [-smirks <string> | -rxn <rfile>] -reactants <infile> [-product <outfile>]
!CATEGORY "input/output options"

  !PARAMETER -smirks
    !ALIAS -s
    !TYPE string
    !VISIBILITY simple
    !BRIEF SMIRKS reaction string
  !END

  !PARAMETER -rxn
    !TYPE string
    !VISIBILITY simple
    !BRIEF MDL reaction file
  !END

  !PARAMETER -reactants
    !ALIAS -r
    !TYPE string
    !LIST true
    !REQUIRED true
    !VISIBILITY simple
    !BRIEF list of input reactant filenames
  !END

  !PARAMETER -product
    !ALIAS -p
    !TYPE string
    !REQUIRED false
    !VISIBILITY simple
    !BRIEF output product filename
  !END
!END

!CATEGORY "OELibraryGen options"

  !PARAMETER -relax
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF unmapped atoms on reactant side are not deleted during reaction
  !END

  !PARAMETER -implicitH
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF reaction will be perfomed using implicit hydrogens
  !END

  !PARAMETER -valence
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF automatic valence correction will be applied
  !END

!END

!CATEGORY "product smiles generation options"

  !PARAMETER -unique
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF only unique product canonical smiles will be written
  !END

  !PARAMETER -isomeric
    !TYPE bool
    !REQUIRED false
    !DEFAULT false
    !VISIBILITY simple
    !BRIEF include atom and bond stereochemistry in product smiles string
  !END

!END
"""
if __name__ == "__main__":
    sys.exit(main(sys.argv))
