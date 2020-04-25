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
    itf = oechem.OEInterface()
    if not SetupInterface(argv, itf):
        return 1

    ifs = oechem.oemolistream()
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))

    ofs = oechem.oemolostream()
    if not ofs.open(itf.GetString("-out")):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-out"))

    logfile = oechem.oeout
    if itf.HasString("-log"):
        if not logfile.open(itf.GetString("-log")):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % itf.GetString("-log"))

    # Szybki options
    opts = oeszybki.OESzybkiOptions()

    # select run type
    if itf.GetBool("-t"):
        opts.SetRunType(oeszybki.OERunType_TorsionsOpt)
    if itf.GetBool("-n"):
        opts.SetRunType(oeszybki.OERunType_SinglePoint)

    # apply solvent model
    if itf.GetBool("-s"):
        opts.GetSolventOptions().SetSolventModel(oeszybki.OESolventModel_Sheffield)

    # remove attractive VdW forces
    if itf.GetBool("-a"):
        opts.GetGeneralOptions().SetRemoveAttractiveVdWForces(True)

    # Szybki object
    sz = oeszybki.OESzybki(opts)

    # fix atoms
    if itf.HasString("-f"):
        if not sz.FixAtoms(itf.GetString("-f")):
            oechem.OEThrow.Warning("Failed to fix atoms for %s" % itf.GetString("-f"))

    # process molecules
    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, mol):
        logfile.write("\nMolecule %s\n" % mol.GetTitle())
        no_res = True
        for results in sz(mol):
            results.Print(logfile)
            no_res = False

        if no_res:
            oechem.OEThrow.Warning("No results processing molecule: %s" % mol.GetTitle())
            continue
        else:
            oechem.OEWriteMolecule(ofs, mol)

    return 0


InterfaceData = """
!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input molecule file name.
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

!PARAMETER -s
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF Optimization in solution.
!END

!PARAMETER -t
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF Optimization of torsions.
!END

!PARAMETER -n
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF Single point calculation.
!END

!PARAMETER -a
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF No attractive VdW forces.
!END

!PARAMETER -f
  !TYPE string
  !REQUIRED false
  !BRIEF SMARTS pattern of fixed atoms.
!END
"""


def SetupInterface(argv, itf):
    oechem.OEConfigure(itf, InterfaceData)
    if oechem.OECheckHelp(itf, argv):
        return False
    if not oechem.OEParseCommandLine(itf, argv):
        return False
    if not oechem.OEIsReadable(oechem.OEGetFileType(
                  oechem.OEGetFileExtension(itf.GetString("-in")))):
        oechem.OEThrow.Warning("%s is not a readable input file" % itf.GetString("-in"))
        return False
    if not oechem.OEIsWriteable(oechem.OEGetFileType(
                  oechem.OEGetFileExtension(itf.GetString("-out")))):
        oechem.OEThrow.Warning("%s is not a writable output file" % itf.GetString("-out"))
        return False
    return True


if __name__ == "__main__":
    sys.exit(main(sys.argv))
