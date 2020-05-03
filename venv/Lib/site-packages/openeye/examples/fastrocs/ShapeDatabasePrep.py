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

# Cache as much as possible on the molecule to improve the performance
# of starting a server from scratch. Also cull to desired number of
# conformers if requested.

import os
import sys

from openeye import oechem
from openeye import oefastrocs

oepy = os.path.join(os.path.dirname(__file__), "..", "python")
sys.path.insert(0, os.path.realpath(oepy))

InterfaceData = """\
!BRIEF [-maxConfs 10] [-storeFloat] [-in] <database.oeb> [-out] <database.oeb>
!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Input database to prep
  !KEYLESS 1
!END
!PARAMETER -out
  !TYPE string
  !REQUIRED true
  !BRIEF Output prepared database
  !KEYLESS 2
!END
!PARAMETER -maxConfs
  !ALIAS -mc
  !TYPE int
  !DEFAULT 10
  !REQUIRED false
  !BRIEF Maximum conformers per molecule
!END
!PARAMETER -storeFloat
  !ALIAS -sf
  !TYPE bool
  !DEFAULT false
  !REQUIRED false
  !BRIEF Store as full float precision in output file else store as half float (default)
!END
"""


def TrimConformers(mol, maxConfs):
    for i, conf in enumerate(mol.GetConfs()):
        if i >= maxConfs:
            mol.DeleteConf(conf)


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    # input - preserve rotor-offset-compression
    ifs = oechem.oemolistream()
    oechem.OEPreserveRotCompress(ifs)
    if not ifs.open(itf.GetString("-in")):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % itf.GetString("-in"))

    # output - use PRE-compress for smaller files (no need to .gz the file)
    ofs = oechem.oemolostream()
    oechem.OEPRECompress(ofs)
    if not ofs.open(itf.GetString("-out")):
        oechem.OEThrow.Fatal("Unable to open '%s' for writing" % itf.GetString("-out"))
    if itf.GetString("-out").endswith('.gz'):
        oechem.OEThrow.Fatal("Output file must not gzipped")

    maxConfs = itf.GetInt("-maxConfs")
    if maxConfs < 1:
        oechem.OEThrow.Fatal("Illegal number of conformer requested %u", maxConfs)

    dots = oechem.OEDots(10000, 200, "molecules")
    for mol in ifs.GetOEMols():
        if maxConfs is not None:
            TrimConformers(mol, maxConfs)

        oefastrocs.OEPrepareFastROCSMol(mol)
        if not itf.GetBool("-storeFloat"):
            halfMol = oechem.OEMol(mol, oechem.OEMCMolType_HalfFloatCartesian)
            oechem.OEWriteMolecule(ofs, halfMol)
        else:
            oechem.OEWriteMolecule(ofs, mol)

        dots.Update()

    dots.Total()
    ofs.close()

    print("Indexing %s" % itf.GetString("-out"))
    if not oechem.OECreateMolDatabaseIdx(itf.GetString("-out")):
        oechem.OEThrow.Fatal("Failed to index %s" % itf.GetString("-out"))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
