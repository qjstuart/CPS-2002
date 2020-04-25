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
from openeye import oespicoli


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <protein> <ligand>" % args[0])

    pifs = oechem.oemolistream()
    if not pifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading protein." % args[1])

    prot = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(pifs, prot):
        oechem.OEThrow.Fatal("Unable to read protein")

    oechem.OEAddExplicitHydrogens(prot)
    oechem.OEAssignBondiVdWRadii(prot)

    lifs = oechem.oemolistream()
    if not lifs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for reading ligand." % args[2])

    lig = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(lifs, lig):
        oechem.OEThrow.Fatal("Unable to read ligand")

    oechem.OEAddExplicitHydrogens(lig)
    oechem.OEAssignBondiVdWRadii(lig)

    comp = oechem.OEGraphMol(prot)
    oechem.OEAddMols(comp, lig)

    compSurf = oespicoli.OESurface()
    oespicoli.OEMakeMolecularSurface(compSurf, comp)

    protSurf = oespicoli.OESurface()
    oespicoli.OEMakeMolecularSurface(protSurf, prot)

    ligSurf = oespicoli.OESurface()
    oespicoli.OEMakeMolecularSurface(ligSurf, lig)

    compVol = oespicoli.OESurfaceVolume(compSurf)
    protVol = oespicoli.OESurfaceVolume(protSurf)
    ligVol = oespicoli.OESurfaceVolume(ligSurf)
    oespicoli.OEWriteSurface("comp.oesrf", compSurf)
    oespicoli.OEWriteSurface("prot.oesrf", protSurf)
    oespicoli.OEWriteSurface("lig.oesrf", ligSurf)

    oechem.OEThrow.Info("%s-%s: dV(C-P) = %.1f V(L) = %.1f V(C) = %.1f V(P) = %.1f" %
                        (prot.GetTitle(), lig.GetTitle(),
                         compVol - protVol, ligVol, compVol, protVol))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
