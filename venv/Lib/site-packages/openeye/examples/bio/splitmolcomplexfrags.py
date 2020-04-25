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
# Split a mol complex (a PDB structure, for example) into fragments
#############################################################################

import sys
from openeye import oechem


def main(argv=[__name__]):

    itf = oechem.OEInterface(InterfaceData)
    oechem.OEConfigureSplitMolComplexOptions(itf)

    if not oechem.OEParseCommandLine(itf, argv):
        oechem.OEThrow.Fatal("Unable to interpret command line!")

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

    if itf.GetBool("-verbose"):
        # don't bother counting sites unless we're going to print them
        numSites = oechem.OECountMolComplexSites(inmol, opts)
        oechem.OEThrow.SetLevel(oechem.OEErrorLevel_Verbose)
        oechem.OEThrow.Verbose("sites %d" % numSites)

    for frag in oechem.OEGetMolComplexComponents(inmol, opts):
        oechem.OEThrow.Verbose("frag %s" % frag.GetTitle())
        oechem.OEWriteMolecule(oms, frag)

    oms.close()

#############################################################################
# INTERFACE
#############################################################################


InterfaceData = '''
!BRIEF splitmolcomplexfrags.py <inmol> [<outmol>]

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
      !BRIEF If true, show fragment titles and number of binding sites
      !VISIBILITY simple
      !REQUIRED false
   !END
!END
'''

if __name__ == "__main__":
    sys.exit(main(sys.argv))
