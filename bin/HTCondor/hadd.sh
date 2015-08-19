#!/bin/bash

# This script hadds files stored in /hdfs by making the output on some local area
# (since we can't stream to hdfs) then transfers output back to hdfs
# Mainly for use on Condor.
#
# Usage:
#     ./hadd.sh <output filename with full path> <input files>
#
# (i.e. the same way hadd normally works.)

# setup CMSSW to get ROOT
VER=CMSSW_7_4_2
echo "Setting up ${VER} ..."
echo "... sourcing CMS default environment from CVMFS"
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "... creating CMSSW project area"
scramv1 project CMSSW ${VER}
cd ${VER}/src
eval `scramv1 runtime -sh`
echo "${VER} has been set up"

# the hadding bit
echo "$@"
outputFile="$1"
echo "Output file"
echo "$outputFile"
shift;
inputFiles=$@
echo "Input files"
echo $inputFiles
timeNow=`date +"%H%M%S"`
tmpName="temp_${timeNow}.root"
echo "Making temp file $tmpName"
echo "Will make output $outputFile"
hadd "$tmpName" ${inputFiles[@]}
hadoop fs -copyFromLocal -f "$tmpName" "${outputFile#/hdfs}"
rm "$tmpName"
