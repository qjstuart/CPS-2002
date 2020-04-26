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

from openeye import oechem
from openeye import oeshape


def main(argv=[__name__]):
    if len(argv) != 2:
        oechem.OEThrow.Usage("%s <infile>" % argv[0])

    ifs = oechem.oemolistream(argv[1])

    for mol in ifs.GetOEGraphMols():
        oechem.OEThrow.Info("              Title: %s" % mol.GetTitle())
        oechem.OEThrow.Info("             Volume: %8.2f" % oeshape.OECalcVolume(mol))
        oechem.OEThrow.Info("Volume: (without H): %8.2f\n" % oeshape.OECalcVolume(mol, False))

        smult = oeshape.OECalcShapeMultipoles(mol)

        oechem.OEThrow.Info("  Steric multipoles:")
        oechem.OEThrow.Info("           monopole: %8.2f" % smult[0])
        oechem.OEThrow.Info("        quadrupoles: %8.2f %8.2f %8.2f"
                            % (smult[1], smult[2], smult[3]))
        oechem.OEThrow.Info("          octopoles:")
        oechem.OEThrow.Info("                xxx: %8.2f  yyy: %8.2f  zzz: %8.2f"
                            % (smult[4], smult[5], smult[6]))
        oechem.OEThrow.Info("                xxy: %8.2f  xxz: %8.2f  yyx: %8.2f"
                            % (smult[7], smult[8], smult[9]))
        oechem.OEThrow.Info("                yyz: %8.2f  zzx: %8.2f  zzy: %8.2f"
                            % (smult[10], smult[11], smult[12]))
        oechem.OEThrow.Info("                xyz: %8.2f\n" % smult[13])


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
