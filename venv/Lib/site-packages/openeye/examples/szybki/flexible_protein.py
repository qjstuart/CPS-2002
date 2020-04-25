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

import sys

from openeye import oechem
from openeye import oeszybki


def main(argv=[__name__]):
    itf = oechem.OEInterface(Interface, argv)

    lfs = oechem.oemolistream()
    if not lfs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))

    pfs = oechem.oemolistream()
    if not pfs.open(itf.GetString("-p")):
        oechem.OEThrow.Fatal("Unable to open %s for reading", itf.GetString("-p"))

    olfs = oechem.oemolostream()
    if not olfs.open(itf.GetString("-out")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-out"))

    opfs = oechem.oemolostream()
    if itf.HasString("-s"):
        if not opfs.open(itf.GetString("-s")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-s"))

    logfile = oechem.oeout
    if itf.HasString("-log"):
        if not logfile.open(itf.GetString("-log")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-log"))

    # Szybki options
    opts = oeszybki.OESzybkiOptions()

    # select optimization type
    opt = itf.GetString("-opt")
    if opt == "Cartesian":
        opts.SetRunType(oeszybki.OERunType_CartesiansOpt)
    if opt == "Torsion":
        opts.SetRunType(oeszybki.OERunType_TorsionsOpt)
    if opt == "SolidBody":
        opts.SetRunType(oeszybki.OERunType_SolidBodyOpt)

    # select protein-electrostatic model
    emodel = itf.GetString("-e")
    elecModel = oeszybki.OEProteinElectrostatics_NoElectrostatics
    if emodel == "VdW":
        elecModel = oeszybki.OEProteinElectrostatics_NoElectrostatics
    elif emodel == "PB":
        elecModel = oeszybki.OEProteinElectrostatics_GridPB
    elif emodel == "Coulomb":
        elecModel = oeszybki.OEProteinElectrostatics_GridCoulomb
    elif emodel == "ExactCoulomb":
        elecModel = oeszybki.OEProteinElectrostatics_ExactCoulomb
    opts.GetProteinOptions().SetProteinElectrostaticModel(elecModel)

    # use smooth potential and tight convergence
    if (emodel == "VdW" or emodel == "ExactCoulomb"):
        opts.GetProteinOptions().SetExactVdWProteinLigand(True)
        opts.GetOptOptions().SetMaxIter(1000)
        opts.GetOptOptions().SetGradTolerance(1e-6)

    # protein flexibility
    opts.GetProteinOptions().SetProteinFlexibilityType(oeszybki.OEProtFlex_SideChains)
    opts.GetProteinOptions().SetProteinFlexibilityRange(itf.GetDouble("-d"))

    # Szybki object
    sz = oeszybki.OESzybki(opts)

    # read and setup protein
    protein = oechem.OEGraphMol()
    oprotein = oechem.OEGraphMol()  # optimized protein
    oechem.OEReadMolecule(pfs, protein)
    sz.SetProtein(protein)

    # process molecules
    for mol in lfs.GetOEMols():
        logfile.write("\nMolecule %s\n" % mol.GetTitle())
        for res in sz(mol):
            res.Print(logfile)

        oechem.OEWriteMolecule(olfs, mol)
        if itf.HasString("-s"):
            sz.GetProtein(oprotein)
            oechem.OEWriteMolecule(opfs, oprotein)

    return 0


Interface = """
!BRIEF -in input_molecule -p protein -out output_molecule
!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input molecule file name.
!END

!PARAMETER -p
  !TYPE string
  !REQUIRED true
  !BRIEF Input protein file name.
!END

!PARAMETER -out
  !TYPE string
  !REQUIRED true
  !BRIEF Output molecule file name.
!END

!PARAMETER -log
  !TYPE string
  !REQUIRED false
  !BRIEF Log file name. Defaults to standard out.
!END

!PARAMETER -e
  !TYPE string
  !DEFAULT VdW
  !LEGAL_VALUE VdW
  !LEGAL_VALUE PB
  !LEGAL_VALUE Coulomb
  !LEGAL_VALUE ExactCoulomb
  !BRIEF Protein ligand electrostatic model.
!END

!PARAMETER -opt
  !TYPE string
  !DEFAULT Cartesian
  !LEGAL_VALUE Cartesian
  !LEGAL_VALUE Torsion
  !LEGAL_VALUE SolidBody
  !BRIEF Optimization method
!END

!PARAMETER -d
  !TYPE double
  !DEFAULT 5.0
  !BRIEF Distance criteria from protein side-chains flexibility.
!END

!PARAMETER -s
  !TYPE string
  !REQUIRED false
  !BRIEF File name the partially optimized protein will be saved.
!END
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
