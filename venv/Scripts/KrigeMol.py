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
from math import log10
from math import sqrt
from math import pow

from openeye import oechem
from openeye import oestats
from openeye import oedepict


def GetColorDict():
    colorMap = {}
    colorMap["red"] = oechem.OERed
    colorMap["green"] = oechem.OEGreen
    colorMap["blue"] = oechem.OEBlue
    colorMap["yellow"] = oechem.OEYellow
    colorMap["cyan"] = oechem.OECyan
    colorMap["magenta"] = oechem.OEMagenta
    colorMap["orange"] = oechem.OEOrange
    colorMap["pink"] = oechem.OEPink
    colorMap["grey"] = oechem.OEPurple
    colorMap["royalblue"] = oechem.OERoyalBlue
    colorMap["olivebrown"] = oechem.OEOliveBrown
    colorMap["olivegreen"] = oechem.OEOliveGreen
    colorMap["oliveGrey"] = oechem.OEOliveGrey
    colorMap["limegreen"] = oechem.OELimeGreen
    colorMap["darkblue"] = oechem.OEDarkBlue
    colorMap["darkgreen"] = oechem.OEDarkGreen
    colorMap["darkblue"] = oechem.OEDarkBlue
    colorMap["darkyellow"] = oechem.OEDarkYellow
    colorMap["darkcyan"] = oechem.OEDarkCyan
    colorMap["darkmagenta"] = oechem.OEDarkMagenta
    colorMap["darkorange"] = oechem.OEDarkOrange
    colorMap["darkgrey"] = oechem.OEDarkGrey
    colorMap["darkrose"] = oechem.OEDarkRose
    colorMap["darkbrown"] = oechem.OEDarkBrown
    colorMap["darksalmon"] = oechem.OEDarkSalmon
    colorMap["darkpurple"] = oechem.OEDarkPurple
    colorMap["mediumbrown"] = oechem.OEMediumBrown
    colorMap["mediumBlue"] = oechem.OEMediumBlue
    colorMap["mediumyellow"] = oechem.OEMediumYellow
    colorMap["mediumgreen"] = oechem.OEMediumGreen
    colorMap["mediumorange"] = oechem.OEMediumOrange
    colorMap["mediumpurple"] = oechem.OEMediumPurple
    colorMap["mediumsalmon"] = oechem.OEMediumSalmon
    colorMap["lightblue"] = oechem.OELightBlue
    colorMap["lightgrey"] = oechem.OELightGrey
    colorMap["lightpurple"] = oechem.OELightPurple
    colorMap["lightsalmon"] = oechem.OELightSalmon
    colorMap["lightbrown"] = oechem.OELightBrown
    colorMap["lightorange"] = oechem.OELightOrange
    colorMap["lightgreen"] = oechem.OELightGreen
    colorMap["bluetint"] = oechem.OEBlueTint
    colorMap["brown"] = oechem.OEBrown
    colorMap["mandarin"] = oechem.OEMandarin
    colorMap["greenblue"] = oechem.OEGreenBlue
    colorMap["greentint"] = oechem.OEGreenTint
    colorMap["hotpink"] = oechem.OEHotPink
    colorMap["pinktint"] = oechem.OEPinkTint
    colorMap["redorange"] = oechem.OERedOrange
    colorMap["seagreen"] = oechem.OESeaGreen
    colorMap["skyblue"] = oechem.OESkyBlue
    colorMap["violet"] = oechem.OEViolet
    colorMap["yellowtint"] = oechem.OEYellowTint
    colorMap["copper"] = oechem.OECopper
    colorMap["gold"] = oechem.OEGold
    colorMap["silver"] = oechem.OESilver
    colorMap["pewter"] = oechem.OEPewter
    colorMap["brass"] = oechem.OEBrass
    return colorMap


def OEAddParameterColors(itf, flag):
    param = itf.GetParameter(flag)
    colorMap = GetColorDict()
    for key in colorMap:
        param.AddLegalValue(key)


def OETextToColor(text):
    colorMap = GetColorDict()
    return colorMap[text]


def OEGetFilename(itf, flag):
    prefix = itf.GetString("-prefix")
    param = itf.GetParameter(flag)
    if param.GetHasValue():
        return itf.GetString(flag)
    else:
        return prefix + "_" + itf.GetString(flag)


def OEIsUnmeasured(itf, val):
    if itf.HasDouble("-unmeasured_greater"):
        uVal = itf.GetDouble("-unmeasured_greater")
        if itf.GetBool("-krige_log"):
            uVal = log10(uVal)
        if val > uVal:
            return True

    if itf.HasDouble("-unmeasured_less"):
        uVal = itf.GetDouble("-unmeasured_less")
        if itf.GetBool("-krige_log"):
            uVal = log10(uVal)
        if val < uVal:
            return True
    iVal = 0
    while itf.HasDouble("-unmeasured_values", iVal):
        uVal = itf.GetDouble("-unmeasured_values", iVal)
        if itf.GetBool("-krige_log"):
            uVal = log10(uVal)
        if val == uVal:
            return True
        iVal += 1
    return False


def main(argv=[__name__]):
    itf = oechem.OEInterface()
    oechem.OEConfigure(itf, Interface)
    OEAddParameterColors(itf, "-atom_contribution_positive_color")
    OEAddParameterColors(itf, "-atom_contribution_negative_color")
    OEAddParameterColors(itf, "-classification_colors")
    if not oechem.OEParseCommandLine(itf, argv):
        return 1

    # Figure out output file name
    outFile = OEGetFilename(itf, "-molecule_file")
    reportFile = OEGetFilename(itf, "-report_file")
    failTrainFile = OEGetFilename(itf, "-training_fail_file")
    failKrigeFile = OEGetFilename(itf, "-prediction_fail_file")
    settingsFile = OEGetFilename(itf, "-settings_file")

    # Write the settings file and splash to screen
    oechem.OEWriteSettings(itf, oechem.oeout, False)
    ofs = oechem.oeofstream(settingsFile)
    oechem.OEWriteSettings(itf, ofs, True)
    ofs.close()

    # Setup report options
    rOpts = oestats.OEKrigeReportOptions()
    if itf.HasString("-report_title"):
        rOpts.SetTitle(itf.GetString("-report_title"))
    if itf.HasString("-response_name"):
        rOpts.SetResponseName(itf.GetString("-response_name"))
        responseName = itf.GetString("-response_name")
    else:
        rOpts.SetResponseName(itf.GetString("-response_tag"))
        responseName = itf.GetString("-response_tag")
    if itf.HasString("-atom_contribution_negative_color"):
        color = OETextToColor(itf.GetString("-atom_contribution_negative_color"))
        rOpts.SetContributionNegativeColor(color)
    if itf.HasString("-atom_contribution_positive_color"):
        color = OETextToColor(itf.GetString("-atom_contribution_positive_color"))
        rOpts.SetContributionPositiveColor(color)
    iExtra = 0
    while itf.HasString("-report_tagged_data", iExtra):
        rOpts.PushSDProperty(itf.GetString("-report_tagged_data", iExtra))
        iExtra += 1
    iClass = 0
    while itf.HasDouble("-classification_boundries", iClass):
        boundry = itf.GetDouble("-classification_boundries", iClass)
        if itf.GetBool("-krige_log"):
            boundry = log10(boundry)
        rOpts.PushClassificationBoundry(boundry)
        iClass += 1
    iClass = 0
    while itf.HasString("-classification_colors", iClass):
        color = OETextToColor(itf.GetString("-classification_colors", iClass))
        rOpts.PushClassificationColor(color)
        iClass += 1
    if itf.GetBool("-hide_krige_details"):
        rOpts.SetShowKrigeDetails(False)
    else:
        rOpts.SetShowKrigeDetails(True)
    rOpts.SetUnlog(itf.GetBool("-krige_log"))
    rOpts.SetShowConfidence(itf.GetBool("-show_response_confidence"))
    rOpts.SetResponseSignificantFigures(itf.GetUnsignedInt("-report_significant_figures"))
    if itf.HasString("-atom_contribution_positive_label"):
        rOpts.SetContributionPositiveLabel(itf.GetString("-atom_contribution_positive_label"))
    if itf.HasString("-atom_contribution_negative_label"):
        rOpts.SetContributionNegativeLabel(itf.GetString("-atom_contribution_negative_label"))
    if itf.HasDouble("-atom_contribution_baseline_response"):
        baseline = itf.GetDouble("-atom_contribution_baseline_response")
        if itf.GetBool("-krige_log"):
            baseline = log10(baseline)
            rOpts.SetContributionBaseline(baseline)

    # Figure out the trend properties for universal kriging if we have them
    universalProps = oechem.OEMolPropertyList()
    iProp = 0
    while itf.HasString("-universal_prop", iProp):
        propStr = itf.GetString("-universal_prop", iProp)
        if propStr == "mw":
            universalProps.Add(oestats.OEMolecularWeightPropertyFxn())
            rOpts.PushProperty(oestats.OEMolecularWeightPropertyFxn(), "Molecular Weight")
        else:
            oechem.OEThrow.Error("Unknow property (%s) passed to -universal_prop" % propStr)
        iProp += 1

    # Setup the object for getting the response from the training molecules
    responseFxn = oechem.OEMolTaggedPropertyFxn(itf.GetString("-response_tag"))
    if itf.GetBool("-krige_log"):
        responseFxn = oestats.OEMolLog10PropertyFxn(responseFxn)

    # Construct the krige
    if itf.HasUnsignedInt("-local_krige"):
        opts = oestats.OELocalKrigeOptions()
        opts.SetNumLocal(itf.GetUnsignedInt("-local_krige"))
    else:
        opts = oestats.OEGlobalKrigeOptions()

    # Set if the distance function is stereo aware
    distOpts = oestats.OEDefaultKrigeDistanceOptions()
    distOpts.SetStereoAware(not itf.GetBool("-ignore_stereo"))

    krige = oestats.OEMolKrige(distOpts, universalProps, opts)

    # Add the training molecules to the Krige
    print("Reading in training molecules")
    sw = oechem.OEStopwatch()
    failStr = None
    numTrain = 0
    numTrainFail = 0
    numTrainUnmeasured = 0
    numTrainMeasured = 0
    for trainFile in itf.GetStringList("-train"):
        imstr = oechem.oemolistream(trainFile)
        for mol in imstr.GetOEMols():
            success = False
            # measured = True
            if responseFxn.Has(mol):
                response = responseFxn.Get(mol)
                if OEIsUnmeasured(itf, response):
                    numTrainUnmeasured += 1
                    # measured = False
                    success = krige.AddUnmeasuredTraining(mol, response)
                else:
                    numTrainMeasured += 1
                    success = krige.AddTraining(mol, response)
                numTrain += 1
            if not success:
                numTrainFail += 1
                if failStr is None:
                    failStr = oechem.oemolostream(failTrainFile)
                oechem.OEWriteMolecule(failStr, mol)
            if sw.Elapsed() > 10.0:
                sw.Start()
                if numTrainFail != 0:
                    print("So far added %d training molecules, and of those \
                          %d unmeasured are unmeasured.  "
                          "%d input molecules are missing response data or \
                          universal krige properties."
                          % (numTrain, numTrainUnmeasured, numTrainFail))
                else:
                    print("So far added %d training molecules, and of those \
                          %d unmeasured are unmeasured."
                          % (numTrain, numTrainUnmeasured))
        imstr.close()
    if failStr is not None:
        failStr.close()
        print("Training failed molecules written to %s" % failTrainFile)
    if numTrainFail != 0:
        print("Added %d training molecules, and of those %d unmeasured are unmeasured.  "
              "%d input molecules are missing response data or universal krige properties."
              % (numTrain, numTrainUnmeasured, numTrainFail))
    else:
        print("Added %d training molecules, and of those %d unmeasured are unmeasured."
              % (numTrain, numTrainUnmeasured))

    # Train the Krige on the molecules we added
    print("Training krige model")
    if krige.Train():
        print("Training successful")
    else:
        print("Training failed, aborting")
        return

    # Krige for MW of the test molecules, and compare to actual MW
    krigeTag = "Krige(%s)" % responseName
    upperTag = "Krige(%s) 95%% confidence upper" % responseName
    lowerTag = "Krige(%s) 95%% confidence lower" % responseName

    print("Predicting %s of input molecules" % responseName)
    numKrige = 0
    numKrigeFail = 0
    outstr = oechem.oemolostream(outFile)
    multi = oedepict.OEMultiPageImageFile(oedepict.OEPageOrientation_Landscape,
                                          oedepict.OEPageSize_US_Letter)
    failStr = None
    sw.Start()
    for molFile in itf.GetStringList("-in"):
        imstr = oechem.oemolistream(molFile)
        for mol in imstr.GetOEMols():
            result = krige.GetResult(mol)
            success = True
            if result.Valid():
                response = result.GetResponse()
                conf95 = 1.96*sqrt(result.GetVariance())
                upper95 = response + conf95
                lower95 = response - conf95
                if itf.GetBool("-krige_log"):
                    response = pow(10.0, response)
                    upper95 = pow(10.0, upper95)
                    lower95 = pow(10.0, lower95)
                oechem.OESetSDData(mol, krigeTag, str(response))
                oechem.OESetSDData(mol, upperTag, str(upper95))
                oechem.OESetSDData(mol, lowerTag, str(lower95))
                if not itf.GetBool("-no_report"):
                    oestats.OEKrigeRenderReport(multi.NewPage(), result, mol, rOpts)
                oechem.OEWriteMolecule(outstr, mol)
            else:
                success = False
            numKrige += 1
            if not success:
                numKrigeFail += 1
                failStr = oechem.oemolostream(failKrigeFile)
                oechem.OEWriteMolecule(failStr, mol)
            if sw.Elapsed() > 10.0:
                print("Kriging predicted %d molecules (%d failures) so far"
                      % (numKrige, numKrigeFail))
                sw.Start()
        imstr.close()
    outstr.close()
    if failStr is not None:
        failStr.close()
    print("Kriging predicted %d molecules (%d failures)" % (numKrige, numKrigeFail))

    if not itf.GetBool("-no_report"):
        print("Writing report to %s" % reportFile)
        oedepict.OEWriteMultiPageImage(reportFile, multi)
    print("Finished")

    return 0


Interface = """
!CATEGORY "Input" 1

  !PARAMETER -param 0
    !TYPE param_file
    !REQUIRED false
    !SIMPLE false
    !BRIEF Parameter file
  !END

  !PARAMETER -in 1
    !TYPE string
    !LIST true
    !REQUIRED true
    !BRIEF Input molecules to predict
  !END

  !PARAMETER -training
    !ALIAS -train
    !TYPE string
    !LIST true
    !REQUIRED true
    !LEGAL_VALUE *.oeb.gz
    !LEGAL_VALUE *.sdf.gz
    !LEGAL_VALUE *.oeb
    !LEGAL_VALUE *.sdf
    !BRIEF Training molecules for the krige.  \
Response values should be tagged to SD or generic data (see -response_tag).
  !END

!END

!CATEGORY Settings 2
  !PARAMETER -response_tag 1
    !ALIAS -tag
    !ALIAS -response_tag
    !TYPE string
    !REQUIRED true
    !BRIEF SD or generic data tag on the training molecules the Krige will predict.
  !END

  !PARAMETER -krige_log 2
    !ALIAS -log
    !TYPE bool
    !DEFAULT false
    !SIMPLE true
    !BRIEF Krige on the log of the property specified by the -response_tag. \
Commonly used when predicting activity concentration (e.g. IC50).
  !END

  !PARAMETER -local_krige 3
    !ALIAS -krige_local
    !ALIAS -num_local
    !TYPE unsigned
    !SIMPLE true
    !DEFAULT 0
    !BRIEF Number of nearest training molecules to use in the krige. \
           Setting 0 uses all, i.e., global kriging.
  !END

  !PARAMETER -response_name 4
    !ALIAS -name
    !TYPE string
    !REQUIRED false
    !SIMPLE false
    !BRIEF Name of the response.  If not specified the setting of -response_tag will be used.
  !END

  !PARAMETER -ignore_stereo 5
    !TYPE bool
    !DEFAULT false
    !SIMPLE false
    !BRIEF If true the stereoness of atoms will be ignored \
           in the 2d distance function the krige uses.
  !END

  !CATEGORY "Specifying Unmeasured Responses" 6

    !PARAMETER -unmeasured_values 1
      !ALIAS -unmeasured
      !TYPE double
      !REQUIRED false
      !LIST true
      !SIMPLE false
      !BRIEF Response values that will be considered unmeasured.
    !END

    !PARAMETER -unmeasured_greater 2
      !TYPE double
      !REQUIRED false
      !SIMPLE false
      !BRIEF Response values greater than this value will be considered unmeasured
    !END

    !PARAMETER -unmeasured_less 2
      !TYPE double
      !REQUIRED false
      !SIMPLE false
      !BRIEF Response values less than this value will be considered unmeasured
    !END

  !END

  !CATEGORY "Universal kriging" 7

    !BRIEF Universal kriging flags.  They can be used in combination.

    !PARAMETER -universal_tag
      !ALIAS -utag
      !TYPE string
      !LIST true
      !REQUIRED false
      !SIMPLE false
      !BRIEF SD or generic data tags to use as trend properties for universal kriging.
    !END

    !PARAMETER -universal_tag_log
      !ALIAS -utag_log
      !TYPE string
      !LIST true
      !REQUIRED false
      !SIMPLE false
      !BRIEF Same as -universal_tag, except that the log of the values will be used.
    !END

    !PARAMETER -universal_prop
      !ALIAS -uprop
      !TYPE string
      !LIST true
      !REQUIRED false
      !SIMPLE false
      !LEGAL_VALUE mw
      !BRIEF Calculated properties to use as trend properties for universal kriging
    !END

  !END

  !CATEGORY "Report Options" 8

    !PARAMETER -no_report 0
      !TYPE bool
      !DEFAULT false
      !BRIEF Supress creating a report PDF file.
    !END

    !PARAMETER -report_title 1
      !ALIAS -title
      !TYPE string
      !SIMPLE false
      !BRIEF Title that will be printed on the top of each page of the report.
    !END

    !PARAMETER -report_significant_figures 3
      !ALIAS -sigfigs
      !TYPE unsigned
      !SIMPLE false
      !DEFAULT 3
      !BRIEF Number of significant figures to report the response in on the report.
    !END

    !PARAMETER -show_response_confidence 4
      !ALIAS -conf95
      !TYPE bool
      !DEFAULT false
      !SIMPLE false
      !BRIEF Show the 95% confidence interval of the response on the report.
    !END

    !PARAMETER -report_tagged_data 2
      !ALIAS -extra_tags
      !TYPE string
      !REQUIRED false
      !SIMPLE false
      !BRIEF Extra SD/genertic data to include on the report. \
             (Not used by the calculation).
    !END

    !PARAMETER -atom_contribution_positive_color 4
      !ALIAS -positive_color
      !ALIAS -pos_color
      !TYPE string
      !REQUIRED false
      !SIMPLE false
      !BRIEF Color of positive atom contributions on the krige report
    !END

    !PARAMETER -atom_contribution_negative_color 5
      !ALIAS -negative_color
      !ALIAS -neg_color
      !TYPE string
      !REQUIRED false
      !SIMPLE false
      !BRIEF Color of positive atom contributions on the krige report
    !END

    !PARAMETER -atom_contribution_positive_label 6
      !ALIAS -positive_label
      !ALIAS -pos_label
      !TYPE string
      !SIMPLE false
      !REQUIRED false
      !BRIEF Legend label for atoms that contribute positively to the response
    !END

    !PARAMETER -atom_contribution_negative_label 7
      !ALIAS -negative_label
      !ALIAS -neg_label
      !TYPE string
      !SIMPLE false
      !REQUIRED false
      !BRIEF Legend label for atoms that contribute negatively to the response
    !END

    !PARAMETER -atom_contribution_baseline_response 8
      !ALIAS -baseline_response
      !TYPE double
      !SIMPLE false
      !REQUIRED false
      !BRIEF Set the baseline response that is considered neutral for atom contributions.  \
If not specified the predicted response of each molecule is used for atom contributions.
    !END

    !PARAMETER -classification_boundries 9
      !ALIAS -class
      !TYPE double
      !REQUIRED false
      !SIMPLE false
      !LIST true
      !BRIEF Report result will be given in terms of classifcation defined by \
             these response boundry values.
    !END

    !PARAMETER -classification_colors 10
      !ALIAS -class_colors
      !LIST true
      !TYPE string
      !REQUIRED false
      !SIMPLE false
      !BRIEF User specification of the classification colors.  \
The order applies to the classifications is highest to lowest.
    !END

    !PARAMETER -hide_krige_details 11
      !ALIAS -hide_details
      !TYPE bool
      !SIMPLE false
      !DEFAULT false
      !BRIEF Hide the krige details in the report (variogram and model quality).
    !END

  !END

!END

!CATEGORY "Output" 5

  !PARAMETER -prefix 1
    !TYPE string
    !DEFAULT krige
    !SIMPLE true
    !BRIEF Prefix for output files
  !END

  !PARAMETER -molecule_file 2
    !ALIAS -mol_file
    !ALIAS -out
    !TYPE string
    !SIMPLE false
    !DEFAULT molecules.sdf
    !LEGAL_VALUE *.oeb.gz
    !LEGAL_VALUE *.sdf.gz
    !LEGAL_VALUE *.oeb
    !LEGAL_VALUE *.sdf
    !BRIEF Output molecule for molecules with krige predictions tagged to them
  !END

  !PARAMETER -report_file 3
    !ALIAS -report
    !TYPE string
    !DEFAULT report.pdf
    !LEGAL_VALUE *.pdf
    !SIMPLE false
    !BRIEF Report file
  !END

  !PARAMETER -training_fail_file 4
    !ALIAS -train_fail_file
    !TYPE string
    !DEFAULT training_fail.sdf
    !SIMPLE false
    !BRIEF Output file for training molecules that failed to be added to the Krige
  !END

  !PARAMETER -prediction_fail_file 5
    !ALIAS -predict_fail_file
    !TYPE string
    !DEFAULT prediction_fail.sdf
    !SIMPLE false
    !BRIEF Output files for molecules that the Krige failed to predict
  !END

  !PARAMETER -settings_file 6
    !TYPE string
    !DEFAULT settings.txt
    !SIMPLE false
    !BRIEF Output file with parameters settings for this run
  !END

!END

"""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
