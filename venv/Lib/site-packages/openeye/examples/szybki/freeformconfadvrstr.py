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
from openeye import oeszybki


def main(args):
    if len(args) != 3:
        oechem.OEThrow.Usage("%s <input> <output>" % args[0])

    ifs = oechem.oemolistream()
    if not ifs.open(args[1]):
        oechem.OEThrow.Fatal("Unable to open %s for reading" % args[1])

    ofs = oechem.oemolostream()
    if not ofs.open(args[2]):
        oechem.OEThrow.Fatal("Unable to open %s for writing" % args[2])

    mol = oechem.OEMol()
    oechem.OEReadMolecule(ifs, mol)

    opts = oeszybki.OEFreeFormConfOptions()
    ffconf = oeszybki.OEFreeFormConfAdvanced(opts)

    # Make a copy of our MCMol.  We will execute the FreeFormConf commands on
    # the copied molecule so that our original molecule stays intact.
    omol = oechem.OEMol(mol)

    # Make further copies of our original molecule.  The copied molecule(s) would be used
    # as source on which retriction energies would be calculated
    rmol = oechem.OEMol(mol)
    fmol = oechem.OEMol(mol)

    # Prepare a comprehensive ensemble of molecule conformers.  For calculation
    # of restriction energies we want to make sure that all the corresponding free
    # conformers are also part of the comprehensive ensemble.  This will also
    # assign solvent charges on the molecule and check that the ensemble is
    # otherwise ready for FreeFormConf calculations. The resulting `fmol`
    # contains the correspondig free conformers.
    if not (ffconf.PrepareEnsemble(omol, rmol, fmol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Failed to prepare ensemble for FreeFormConf calculations")

    # Perform loose optimization of the ensemble conformers.  We will remove
    # duplicates based on the loose optimization, to reduce the time needed for
    # tighter, more stricter optimization
    if not (ffconf.PreOptimizeEnsemble(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Pre-optimization of the ensembles failed")

    # Remove duplicates from the pre-optimized ensemble
    if not (ffconf.RemoveDuplicates(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Duplicate removal from the ensembles failed")

    # Perform the desired optimization.  This uses a stricter convergence
    # criteria in the default settings.
    if not (ffconf.Optimize(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Optimization of the ensembles failed")

    # Remove duplicates to obtain the set of minimum energy conformers
    if not (ffconf.RemoveDuplicates(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Duplicate removal from the ensembles failed")

    # Perform FreeFormConf free energy calculations.  When all the above steps
    # have already been performed on the ensemble, this energy calculation
    # step is fast.
    if not (ffconf.EstimateEnergies(omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Estimation of FreeFormConf energies failed")

    # Gather results of calculation into a results object for ease of viewing, etc.
    res = oeszybki.OEFreeFormConfResults(omol)
    oechem.OEThrow.Info("Number of unique conformations: %d" % res.GetNumUniqueConfs())
    oechem.OEThrow.Info("Conf.  Delta_G   Vibrational_Entropy")
    oechem.OEThrow.Info("      [kcal/mol]     [J/(mol K)]")
    for r in res.GetResultsForConformations():
        oechem.OEThrow.Info("%2d %10.2f %14.2f" % (r.GetConfIdx(), r.GetDeltaG(),
                                                   r.GetVibrationalEntropy()))

    # Identify the corresponding conformer(s) to the free minimized conformer(s).
    # If identified, the corresponding (Conf)Free energy information is also
    # copied to the free conformers
    if not (ffconf.IdentifyConformer(fmol, omol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Identification of free conformer(s) failed")

    # Estimate restriction energies. Since both restricted and free conformer
    # energy components are already available, this operation is fast.
    if not (ffconf.EstimateRestrictionEnergy(fmol, rmol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Restriction energy estimation failed")

    # Gather restriction energies into a results object for ease of viewing, etc.
    rstrRes = oeszybki.OERestrictionEnergyResult(fmol)
    oechem.OEThrow.Info("Global strain: %f" % rstrRes.GetGlobalStrain())
    oechem.OEThrow.Info("Local strain: %f" % rstrRes.GetLocalStrain())

    # Optionally it is desired to perform a restrained optimization of the
    # restricted conformer(s) to brush out any energy differences due to
    # force field constaints or the sources of coonformer coordinates.  Note: The
    # high level EstimateFreeEnergy method does not perform this opertion.
    if not (ffconf.OptimizeRestraint(rmol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Restraint optimization of the conformer(s) failed")

    # Estimate restriction energies on this optimized conformers.
    # Since both restricted and free conformer energy components
    # are already available, this operation is fast.
    if not (ffconf.EstimateRestrictionEnergy(fmol, rmol) == oeszybki.OEFreeFormReturnCode_Success):
        oechem.OEThrow.Error("Restriction energy estimation failed")

    # Gather restriction energies into a results object for ease of viewing, etc.
    rstrRes = oeszybki.OERestrictionEnergyResult(fmol)
    oechem.OEThrow.Info("Global strain: %f" % rstrRes.GetGlobalStrain())
    oechem.OEThrow.Info("Local strain: %f" % rstrRes.GetLocalStrain())

    oechem.OEWriteMolecule(ofs, omol)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
