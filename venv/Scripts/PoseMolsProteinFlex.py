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

from __future__ import print_function
import sys

from openeye import oechem
from openeye import oedocking


def main(argv=[__name__]):
    itf = oechem.OEInterface(InterfaceData)
    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    imstr = oechem.oemolistream(itf.GetString("-in"))
    omstr = oechem.oemolostream(itf.GetString("-out"))

    receptors = []
    for receptor_filename in itf.GetStringList("-receptors"):
        receptor = oechem.OEGraphMol()
        if not oedocking.OEReadReceptorFile(receptor, receptor_filename):
            oechem.OEThrow.Fatal("Unable to read receptor from %s" %
                                 receptor_filename)
        receptors.append(receptor)

    options = oedocking.OEPositOptions()
    options.SetPoseRelaxMode(oedocking.OEPoseRelaxMode_ALL)
    poser = oedocking.OEPosit(options)
    for receptor in receptors:
        poser.AddReceptor(receptor)

    for mcmol in imstr.GetOEMols():
        print("posing", mcmol.GetTitle())
        result = oedocking.OESinglePoseResult()
        ret_code = poser.Dock(result, mcmol)
        if ret_code == oedocking.OEDockingReturnCode_Success:
            posedMol = result.GetPose()
            oechem.OESetSDData(posedMol, poser.GetName(),
                               str(result.GetProbability()))
            oechem.OESetSDData(posedMol, "Receptor Index",
                               str(result.GetReceptorIndex()))
            oechem.OEWriteMolecule(omstr, posedMol)
            oechem.OEWriteMolecule(omstr, result.GetReceptor())
        else:
            errMsg = oedocking.OEDockingReturnCodeGetName(ret_code)
            oechem.OEThrow.Warning("%s: %s" % (mcmol.GetTitle(), errMsg))
    return 0


InterfaceData = """
!PARAMETER -receptors
  !ALIAS -rec
  !TYPE string
  !LIST true
  !REQUIRED true
  !LEGAL_VALUE *.oeb
  !LEGAL_VALUE *.oeb.gz
  !BRIEF Receptor files the molecules pass to the -in flag will be posed to
!END

!PARAMETER -in
  !TYPE string
  !REQUIRED true
  !BRIEF Multiconformer file of molecules to be posed.
!END

!PARAMETER -out
  !TYPE string
  !REQUIRED true
  !BRIEF Posed molecules will be written to this file
!END
"""

if __name__ == "__main__":
    sys.exit(main(sys.argv))
