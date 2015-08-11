#!/bin/bash

# This script hadds files stored in hdfs by making the output on /user (since we can't stream to hdfs)
# then transfers output back to hdfs
#
# Usage:
#     ./hadd.sh <input dir> <regex of files to match>
#     ./hadd.sh /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE30BX50_newRCTv4_newLUT "L1Tree_*"
#
#

# Can optionally setup CMSSW to get ROOT
# cmssw_version=CMSSW_7_4_6_patch6
# echo "Setting up ${cmssw_version} ..."
# echo "... sourcing CMS default environment from CVMFS"
# source /cvmfs/cms.cern.ch/cmsset_default.sh
# echo "... creating CMSSW project area"
# scramv1 project CMSSW ${cmssw_version}
# cd ${cmssw_version}/src
# eval `scramv1 runtime -sh`
# echo "${cmssw_version} has been set up"

# the hadding bit
inputDir="$1"
fileStem="$2"
timeNow=$(date +"%H%M%S")
tmpName="temp_${timeNow}.root"

echo "hadding files in $inputDir starting with $fileStem"
echo "Making temp file $tmpName"
echo "Will put output in ${inputDir#/hdfs}"

hadd $tmpName $inputDir/$fileStem
hadoop fs -copyFromLocal "$tmpName" "${inputDir#/hdfs}"
rm "$tmpName"