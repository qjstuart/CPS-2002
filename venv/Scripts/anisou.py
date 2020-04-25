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
# Output anisotropic B factor information
#############################################################################
import sys
from openeye import oechem


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData, argv)

    verbose = itf.GetBool("-verbose")
    ifname = itf.GetString("-input")

    ims = oechem.oemolistream()
    if not ims.open(ifname):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % ifname)

    ims.SetFlavor(oechem.OEFormat_PDB, oechem.OEIFlavor_PDB_Default | oechem.OEIFlavor_PDB_DATA)

    for mol in ims.GetOEMols():
        if verbose:
            if not oechem.OEHasResidues(mol):
                oechem.OEPerceiveResidues(mol, oechem.OEPreserveResInfo_All)
            for atom in mol.GetAtoms():
                res = oechem.OEAtomGetResidue(atom)

                uij = oechem.OEAnisoUij()
                if oechem.OEGetAnisou(uij, atom):
                    oechem.OEThrow.Info("%s %s%c %s%d%c %c (u11=%5d, u22=%5d, u33=%5d, \
                                        u12=%5d, u13=%5d, u23=%5d)" %
                                        (mol.GetTitle(),
                                         atom.GetName(),
                                         res.GetAlternateLocation(),
                                         res.GetName(),
                                         res.GetResidueNumber(),
                                         res.GetInsertCode(),
                                         res.GetChainID(),
                                         uij.GetU11(),
                                         uij.GetU22(),
                                         uij.GetU33(),
                                         uij.GetU12(),
                                         uij.GetU13(),
                                         uij.GetU23()))
                else:
                    oechem.OEThrow.Info("%s %s%c %s%d%c %c -no-anisou-" % (mol.GetTitle(),
                                        atom.GetName(),
                                        res.GetAlternateLocation(),
                                        res.GetName(),
                                        res.GetResidueNumber(),
                                        res.GetInsertCode(),
                                        res.GetChainID()))

        oechem.OEThrow.Info("%s %d atoms with anisou data (out of %d)" % (mol.GetTitle(),
                            oechem.OECount(mol, oechem.OEHasAnisou()),
                            mol.NumAtoms()))

    return 0


InterfaceData = """\
!BRIEF [-v] [-i] <mol file>

!CATEGORY "input options"

  !PARAMETER -input
    !ALIAS -i
    !TYPE string
    !REQUIRED true
    !BRIEF input mol file name
    !KEYLESS 1
  !END
!END

!CATEGORY "options"

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
