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


def ReadProteinFromPDB(pdb_file, mol):
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
    if len(argv) not in [3, 5, 6]:
        oechem.OEThrow.Usage("%s <extract protein PDB> <reference protein PDB> [min score] [superpose] [nowrite]" % argv[0])  # noqa

    do_write = True
    if len(argv) == 6:
        if argv[5] != "nowrite":
            oechem.OEThrow.Warning("%s is not a valid option.\n" % argv[5])
            sys.exit(1)
        else:
            do_write = False

    opts = oespruce.OEBioUnitExtractionOptions()
    if len(argv) >= 5:
        opts.SetMinScore(int(argv[3]))
        opts.SetSuperpose(bool(argv[4]))

    extract_prot_file = argv[1]
    extract_prot = oechem.OEGraphMol()
    extract_success = ReadProteinFromPDB(extract_prot_file, extract_prot)
    if not extract_success:
        oechem.OEThrow.Fatal("Unable to extract protein(s) from PDB file.")

    ref_prot_file = argv[2]
    ref_prot = oechem.OEGraphMol()
    ref_success = ReadProteinFromPDB(ref_prot_file, ref_prot)
    if not ref_success:
        oechem.OEThrow.Fatal("Unable to reference protein(s) from PDB file.")

    # @ <SNIPPET-OEExtractBioUnits-REF>
    biounits = oespruce.OEExtractBioUnits(extract_prot, ref_prot, opts)
    # @ </SNIPPET-OEExtractBioUnits-REF>

    if do_write:
        pdb_ext = ".pdb"
        str_pos = extract_prot_file.find(pdb_ext)
        base_name = extract_prot_file[0:str_pos]
        temp_dir = tempfile.mkdtemp()

        for i, biounit in enumerate(biounits):
            output_biounit_file = os.path.join(temp_dir, base_name + "_BU_{}.oeb.gz".format(i))  # noqa
            print("Writing biounit {} to {}".format(i, output_biounit_file))
            ofs = oechem.oemolostream(output_biounit_file)
            oechem.OEWriteMolecule(ofs, biounit)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
