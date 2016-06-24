import os
import sys

# choose the mother directory
# choose the fit type (ie the daughter directory), make sure the same has been selected in runCalibration.py
# set the input file names
# and the output file names (either a test or an append)
# $ python /users/jt15104/CMSSW_8_0_7/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/runCalibFitsLocally.py

# note: bin/binning.py must correspond to the type of data you are using!!!

############################################
# user defined section #####################
############################################
motherDirectory = "26May2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_jbntuples_dr0p25_etaBinningVersion2/"

# must ensure that the runCalibration file is set-up to use the same fit! TODO: automate it?
# daughterDirectory = "runCalib_conventionalFit/"
daughterDirectory = "runCalib_jetMetFit1/"
# daughterDirectory = "runCalib_jetMetFitErr/"

inputFiles = [
				"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsVersion2_PU0to10.root",
				"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsVersion2_PU15to25.root",
				"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsVersion2_PU30to40.root",
				]

# initially output a test file
outputFiles = [
				"testPU0to10.root",
				"testPU15to25.root",
				"testPU30to40.root",
				]

# if you are sure that you wish to append the output onto the input
# outputFiles = inputFiles

############################################
############################################
if len(inputFiles) != len(outputFiles):
	print "number of inputs doesn't equal number of outputs...exiting"
	sys.exit()

for i in range(0, len(inputFiles)):
	inputFiles[i] = "/users/jt15104/local_L1JEC_store/" + motherDirectory + daughterDirectory + inputFiles[i]
	outputFiles[i] = "/users/jt15104/local_L1JEC_store/" + motherDirectory + daughterDirectory + outputFiles[i]
	os.system("python /users/jt15104/CMSSW_8_0_7/src/L1Trigger/L1JetEnergyCorrections/bin/runCalibration.py "
			+ inputFiles[i] + " " + outputFiles[i]
			+ " --redo-correction-fit --inherit-params --stage2")
	print "done " + str(i+1) + " of " + str(len(inputFiles)) + " routines"

print "all done:)"