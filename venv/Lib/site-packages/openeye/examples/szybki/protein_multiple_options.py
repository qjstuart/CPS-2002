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

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-out")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-out"))

    logfile = oechem.oeout
    if itf.HasString("-log"):
        if not logfile.open(itf.GetString("-log")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-log"))

    # Szybki options
    opts = oeszybki.OESzybkiOptions()

    # select optimization type
    if(itf.GetBool("-t")):
        opts.SetRunType(oeszybki.OERunType_TorsionsOpt)
    else:
        opts.SetRunType(oeszybki.OERunType_CartesiansOpt)

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
        opts.GetProteinOptions().SetExactVdWProteinLigand(True)
        opts.GetOptOptions().SetMaxIter(1000)
        opts.GetOptOptions().SetGradTolerance(1e-6)
    opts.GetProteinOptions().SetProteinElectrostaticModel(elecModel)

    # Szybki object
    sz = oeszybki.OESzybki(opts)

    # read and setup protein
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(pfs, protein)
    sz.SetProtein(protein)

    # save or load grid potential
    if(emodel == "PB" or emodel == "Coulomb"):
        if(itf.HasString("-s")):
            sz.SavePotentialGrid(itf.GetString("-s"))
        if(itf.HasString("-l")):
            sz.LoadPotentialGrid(itf.GetString("-l"))

    # process molecules
    for mol in lfs.GetOEMols():
        logfile.write("\nMolecule %s\n" % mol.GetTitle())
        no_res = True
        for res in sz(mol):
            res.Print(logfile)
            no_res = False

        if no_res:
            oechem.OEThrow.Warning("No results processing molecule: %s" % mol.GetTitle())
            continue
        else:
            oechem.OEWriteMolecule(ofs, mol)

    return 0


Interface = """
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

!PARAMETER -t
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF Torsions added to the optimized variables.
!END

!PARAMETER -l
  !TYPE string
  !REQUIRED false
  !BRIEF File name of the potential grid to be read.
!END

!PARAMETER -s
  !TYPE string
  !REQUIRED false
  !BRIEF File name of the potential grid to be saved.
!END
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
