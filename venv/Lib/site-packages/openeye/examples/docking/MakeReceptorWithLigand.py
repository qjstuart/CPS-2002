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
from openeye import oedocking


def main(argv):
    if len(argv) != 3:
        oechem.OEThrow.Usage("MakeReceptorWithLigand.py <protein> <bound ligand>")

    proteinMolStream = oechem.oemolistream(argv[1])
    ligandMolStream = oechem.oemolistream(argv[2])

    # @ <SNIPPET-MAKE-RECEPTOR-WITH-LIGAND-1>
    protein = oechem.OEGraphMol()
    oechem.OEReadMolecule(proteinMolStream, protein)

    ligand = oechem.OEGraphMol()
    oechem.OEReadMolecule(ligandMolStream, ligand)

    receptor = oechem.OEGraphMol()
    oedocking.OEMakeReceptor(receptor, protein, ligand)
    # @ </SNIPPET-MAKE-RECEPTOR-WITH-LIGAND-1>

    oedocking.OEWriteReceptorFile(receptor, "receptor.oeb.gz")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
