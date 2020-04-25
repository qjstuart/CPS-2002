#!/usr/bin/env python
# (C) 2018 OpenEye Scientific Software Inc. All rights reserved.
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
# Simple superimposition of a fit protein on to a reference protein
#############################################################################
import sys
import os
from openeye import oechem
from openeye import oespruce
import tempfile


def ReadFromPDB(pdb_file, mol):
    ifs = oechem.oemolistream()
    ifs.SetFlavor(oechem.OEFormat_PDB, oechem.OEIFlavor_PDB_Default | oechem.OEIFlavor_PDB_DATA | oechem.OEIFlavor_PDB_ALTLOC)  # noqa

    if not ifs.open(pdb_file):
        oechem.OEThrow.Fatal("Unable to open %s for reading." % pdb_file)

    temp_mol = oechem.OEGraphMol()
    if not oechem.OEReadMolecule(ifs, temp_mol):
        oechem.OEThrow.Fatal("Unable to read molecule from %s." % pdb_file)
    ifs.close()

    fact = oechem.OEAltLocationFactory(temp_mol)
    mol.Clear()
    fact.MakePrimaryAltMol(mol)
    return (mol)


def main(argv=[__name__]):
    if len(argv) not in [2, 3]:
        oechem.OEThrow.Usage("{} <input protein PDB> [nowrite]".format(argv[0]))  # noqa

    do_write = True
    if len(argv) == 3:
        if argv[2] != "nowrite":
            oechem.OEThrow.Warning("{} is not a valid option.\n".format(argv[1]))
            sys.exit(1)
        else:
            do_write = False

    bio_system_file = argv[1]
    bio_system = oechem.OEGraphMol()
    input_success = ReadFromPDB(bio_system_file, bio_system)
    if not input_success:
        oechem.OEThrow.Fatal("Unable to input protein from PDB file.")

    # @ <SNIPPET-OEMakeDesignUnits>
    design_units = oespruce.OEMakeDesignUnits(bio_system)
    # @ </SNIPPET-OEMakeDesignUnits>

    if do_write:
        base_name = bio_system_file[:-4]
        temp_dir = tempfile.mkdtemp()

        for i, design_unit in enumerate(design_units):
            output_design_unit_file = os.path.join(temp_dir, base_name + "_DU_{}.oedu".format(i))  # noqa
            print("\nWriting design unit {} to {}".format(i, output_design_unit_file))
            oechem.OEWriteDesignUnit(output_design_unit_file, design_unit)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
