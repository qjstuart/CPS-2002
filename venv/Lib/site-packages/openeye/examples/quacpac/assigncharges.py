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
from openeye import oequacpac


def AssignChargesByName(mol, name):
    if name == "noop":
        return oequacpac.OEAssignCharges(mol, oequacpac.OEChargeEngineNoOp())
    elif name == "mmff" or name == "mmff94":
        return oequacpac.OEAssignCharges(mol, oequacpac.OEMMFF94Charges())
    elif name == "am1bcc":
        return oequacpac.OEAssignCharges(mol, oequacpac.OEAM1BCCCharges())
    elif name == "am1bccnosymspt":
        optimize = True
        symmetrize = True
        return oequacpac.OEAssignCharges(mol,
                                         oequacpac.OEAM1BCCCharges(not optimize, not symmetrize))
    elif name == "amber" or name == "amberff94":
        return oequacpac.OEAssignCharges(mol, oequacpac.OEAmberFF94Charges())
    elif name == "am1bccelf10":
        return oequacpac.OEAssignCharges(mol, oequacpac.OEAM1BCCELF10Charges())
    return False


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    ifs = oechem.oemolistream()

    inputFile = itf.GetString("-in")
    if not ifs.open(inputFile):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % inputFile)

    ofs = oechem.oemolostream()

    outFile = itf.GetString("-out")
    if not ofs.open(outFile):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % outFile)

    chargeName = itf.GetString("-method")

    mol = oechem.OEMol()
    while oechem.OEReadMolecule(ifs, mol):
        if not AssignChargesByName(mol, chargeName):
            oechem.OEThrow.Warning("Unable to assign %s charges to mol %s"
                                   % (chargeName, mol.GetTitle()))
        oechem.OEWriteMolecule(ofs, mol)

    ifs.close()
    ofs.close()

#############################################################################
# INTERFACE
#############################################################################


InterfaceData = '''
!BRIEF AssignCharges.py [-options] <inmol> [<outmol>]

!CATEGORY "input/output options :"
   !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !BRIEF Input molecule
      !VISIBILITY simple
      !REQUIRED true
      !KEYLESS 1
   !END

   !PARAMETER -out
      !ALIAS -o
      !TYPE string
      !DEFAULT oeassigncharges.oeb.gz
      !BRIEF Output molecule (usually an oeb)
      !VISIBILITY simple
      !REQUIRED false
      !KEYLESS 2
   !END
!END

!CATEGORY "Charging options :"
   !PARAMETER -method
      !TYPE string
      !LEGAL_VALUE noop
      !LEGAL_VALUE mmff
      !LEGAL_VALUE mmff94
      !LEGAL_VALUE am1bcc
      !LEGAL_VALUE am1bccnosymspt
      !LEGAL_VALUE amber
      !LEGAL_VALUE amberff94
      !LEGAL_VALUE am1bccelf10
      !DEFAULT mmff94
      !BRIEF which set of charges to apply
      !SIMPLE true
      !REQUIRED false
   !END
!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
