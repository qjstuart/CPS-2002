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
# Performing RMSD calculation between a 3D reference molecule and
# multi-conformation molecules
#############################################################################
import sys
from openeye import oechem


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    if not itf.GetBool("-verbose"):
        oechem.OEThrow.SetLevel(oechem.OEErrorLevel_Warning)

    rfname = itf.GetString("-ref")
    ifname = itf.GetString("-in")

    automorph = itf.GetBool("-automorph")
    heavy = itf.GetBool("-heavyonly")
    overlay = itf.GetBool("-overlay")

    ifs = oechem.oemolistream()
    if not ifs.open(rfname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % rfname)

    rmol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(ifs, rmol):
        oechem.OEThrow.Fatal("Unable to read reference molecule")

    ifs = oechem.oemolistream()
    if not ifs.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifname)

    ofs = oechem.oemolostream()
    if itf.HasString("-out"):
        ofname = itf.GetString("-out")
        if not ofs.open(ofname):
            oechem.OEThrow.Fatal("Unable to open %s for writing" % ofname)
        if not overlay:
            oechem.OEThrow.Warning("Output is the same as input when overlay is false")

    for mol in ifs.GetOEMols():
        oechem.OEThrow.Info(mol.GetTitle())

        rmsds = oechem.OEDoubleArray(mol.GetMaxConfIdx())
        rmtx = oechem.OEDoubleArray(9 * mol.GetMaxConfIdx())
        tmtx = oechem.OEDoubleArray(3 * mol.GetMaxConfIdx())

        # perform RMSD for all confomers
        oechem.OERMSD(rmol, mol, rmsds, automorph, heavy, overlay, rmtx, tmtx)

        for conf in mol.GetConfs():
            cidx = conf.GetIdx()
            oechem.OEThrow.Info("Conformer %i : rmsd = %f" % (cidx, rmsds[cidx]))

            if itf.GetBool("-overlay"):
                oechem.OERotate(conf, rmtx[cidx * 9: cidx * 9 + 9])
                oechem.OETranslate(conf, tmtx[cidx * 3: cidx * 3 + 3])

        if itf.HasString("-out"):
            oechem.OEWriteMolecule(ofs, mol)

    return 0

#############################################################################


InterfaceData = """\
!BRIEF [options] [-ref <mol file>] [-in <mol file>] [-out <mol file>]

!CATEGORY "input/output options"

  !PARAMETER -ref
    !TYPE string
    !REQUIRED true
    !BRIEF input reference mol file name
    !KEYLESS 1
  !END

  !PARAMETER -in
    !ALIAS -i
    !TYPE string
    !REQUIRED true
    !BRIEF input mol file name
    !KEYLESS 2
  !END

  !PARAMETER -out
    !ALIAS -o
    !TYPE string
    !REQUIRED false
    !BRIEF output file name, this implies that -overlay should be true
    !KEYLESS 3
  !END

!END

!CATEGORY "options"

  !PARAMETER -automorph
    !TYPE bool
    !DEFAULT true
    !BRIEF assign best atom association
    !DETAIL
        If false, atoms are associated by order.
        If true, graph isomorphism is determined with symmetry perception.
  !END

  !PARAMETER -overlay
    !TYPE bool
    !DEFAULT true
    !BRIEF Minimize to the smallest RMSD
  !END

  !PARAMETER -heavyonly
    !TYPE bool
    !DEFAULT true
    !BRIEF Ignore hydrogens for RMSD calculation
  !END

  !PARAMETER -verbose
    !ALIAS -v
    !TYPE bool
    !DEFAULT false
    !BRIEF verbose
  !END

!END
"""

#############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))
