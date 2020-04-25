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
# split a mol complex (a PDB structure, for example) using low-level funcs
#############################################################################

import sys
from openeye import oechem


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData)
    oechem.OEConfigureSplitMolComplexOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

    if itf.GetBool("-verbose"):
        oechem.OEThrow.SetLevel(oechem.OEErrorLevel_Verbose)

    iname = itf.GetString("-in")
    oname = itf.GetString("-out")

    ims = oechem.oemolistream()
    if not itf.GetUnsignedInt("-modelnum") == 1:
        ims.SetFlavor(oechem.OEFormat_PDB,
                      oechem.OEGetDefaultIFlavor(oechem.OEFormat_PDB) & ~oechem.OEIFlavor_PDB_ENDM)
    if not ims.open(iname):
        oechem.OEThrow.Fatal("Cannot open input file!")

    oms = oechem.oemolostream()
    if not oms.open(oname):
        oechem.OEThrow.Fatal("Cannot open output file!")

    inmol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(ims, inmol):
        oechem.OEThrow.Fatal("Cannot read input file!")

    opts = oechem.OESplitMolComplexOptions()
    oechem.OESetupSplitMolComplexOptions(opts, itf)

    frags = oechem.OEAtomBondSetVector()
    if not oechem.OEGetMolComplexFragments(frags, inmol, opts):
        oechem.OEThrow.Fatal("Unable to split mol complex from %s" % iname)

    numSites = oechem.OECountMolComplexSites(frags)

    if itf.GetBool("-verbose"):
        oechem.OEThrow.SetLevel(oechem.OEErrorLevel_Verbose)
        oechem.OEThrow.Verbose("sites %d" % numSites)

    lig = oechem.OEGraphMol()
    prot = oechem.OEGraphMol()
    wat = oechem.OEGraphMol()
    other = oechem.OEGraphMol()

    if not oechem.OECombineMolComplexFragments(lig, frags, opts, opts.GetLigandFilter()):
        oechem.OEThrow.Fatal("Unable to split ligand from %s" % iname)

    if not oechem.OECombineMolComplexFragments(prot, frags, opts, opts.GetProteinFilter()):
        oechem.OEThrow.Fatal("Unable to split protein complex from %s" % iname)

    if not oechem.OECombineMolComplexFragments(wat, frags, opts, opts.GetWaterFilter()):
        oechem.OEThrow.Fatal("Unable to split waters from %s" % iname)

    if not oechem.OECombineMolComplexFragments(other, frags, opts, opts.GetOtherFilter()):
        oechem.OEThrow.Fatal("Unable to split other mols from %s" % iname)

    if not lig.NumAtoms() == 0:
        oechem.OEThrow.Verbose("  lig %s" % lig.GetTitle())
        oechem.OEWriteMolecule(oms, lig)

    if not prot.NumAtoms() == 0:
        oechem.OEThrow.Verbose(" prot %s" % prot.GetTitle())
        oechem.OEWriteMolecule(oms, prot)

    if not wat.NumAtoms() == 0:
        oechem.OEThrow.Verbose("  wat %s" % wat.GetTitle())
        oechem.OEWriteMolecule(oms, wat)

    if not other.NumAtoms() == 0:
        oechem.OEThrow.Verbose("other %s" % other.GetTitle())
        oechem.OEWriteMolecule(oms, other)

    oms.close()

#############################################################################
# INTERFACE
#############################################################################


InterfaceData = '''
!BRIEF splitmolcomplexlowlevel.py <inmol> [<outmol>]

!CATEGORY "input/output options :"
   !PARAMETER -in
      !ALIAS -i
      !TYPE string
      !BRIEF Input molecule (usually a pdb file)
      !VISIBILITY simple
      !REQUIRED true
      !KEYLESS 1
   !END

   !PARAMETER -out
      !ALIAS -o
      !TYPE string
      !DEFAULT splitmolcomplex.oeb.gz
      !BRIEF Output molecule (usually an oeb)
      !VISIBILITY simple
      !REQUIRED false
      !KEYLESS 2
   !END
!END

!CATEGORY "Display options :"
   !PARAMETER -verbose
      !ALIAS -v
      !TYPE bool
      !DEFAULT false
      !BRIEF If true, show molecule titles and number of binding sites
      !VISIBILITY simple
      !REQUIRED false
   !END
!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
