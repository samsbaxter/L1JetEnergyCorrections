#!/bin/bash

#################################################
# Script to run cmsRun on condor worker node
#################################################

# Store args
# TODO: replace with getopts
script=$1
dataset=$2
filesPerJob=$3
totalFiles=$4
outputDir=$5
ind=$6 # ind is the job number

worker="$PWD" # top level of worker node
export HOME=$worker # need this if getenv = false

######################
# First setup CMSSW
######################
cmssw_version=CMSSW_7_4_6_patch6
echo "Setting up ${cmssw_version} ..."
echo "... sourcing CMS default environment from CVMFS"
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "... creating CMSSW project area"
scramv1 project CMSSW ${cmssw_version}
cd ${cmssw_version}/src
eval `scramv1 runtime -sh`
echo "${cmssw_version} has been set up"

# Setup your git config, otherwise cannot check stuff out of git
git config --global user.github "raggleton"
git config --global user.name "Robin Aggleton"
git config --global user.email "robin.aggleton@cern.ch"
git config -l
export CMSSW_GIT_REFERENCE="${worker}/.cmsgit-cache"

######################
# Setup packages
# Do whatever you need to make sure all necessary packages are checked out, etc
# git cms-addpkg doesn't work for now :(
######################
# git cms-addpkg L1Trigger/L1TCalorimeter
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
git clone https://github.com/raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections

######################
# Make a wrapper config
# This will setup the input files, output file, and number of events
# Means that the user doesn't have to do anything special to their config file
######################
pyfile="wrapper.py"

echo "import FWCore.ParameterSet.Config as cms" >> $pyfile
echo "import "${script%.py}" as myscript" >> $pyfile

# Setup input files
# Figure out index of files for this jobs
idx=$(($filesPerJob * $ind))
limit=$filesPerJob
if [ $((($ind + 1)*$filesPerJob)) -gt $totalFiles ]
    then
    limit=$(($totalFiles - ($ind * $filesPerJob) ))
fi

# Loop over output from das_client.py, get files, write to wrapper
echo "fileNames = [" >> $pyfile
IFS="
"
for line in $(das_client.py --query="file dataset=$dataset" --limit $limit --idx $idx)
do
    if [[ $line == /store* ]]
    then
        echo "    '"$line"'," >> $pyfile
    fi
done
# remove the last trailing ','
sed -i '$s@,$@@' $pyfile
echo "]" >> $pyfile

# Write more overriding things to wrapper
echo "process = myscript.process" >> $pyfile
echo "process.source.fileNames = cms.untracked.vstring(fileNames)" >> $pyfile
echo "process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))" >> $pyfile
echo "process.TFileService.fileName = cms.string(process.TFileService.fileName.value().replace('.root', '_${ind}.root'))" >> $pyfile
echo "process.output.fileName = cms.string(process.output.fileName.value().replace('.root', '_${ind}.root'))" >> $pyfile

echo ""
echo "Wrapper script:"
echo ""
cat $pyfile
echo ""

# Get Golden JSON
wget https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Cert_246908-251883_13TeV_PromptReco_Collisions15_JSON_v2.txt

######################
# Move the cms config script from top level to CMSSW area and build everything
######################
mv $worker/$script .
scram b -j9
ls

######################
# Now finally run script!
# TODO: some automated retry system
######################
cmsRun $pyfile
echo "CMS JOB OUTPUT" $?

######################
# Copy across to hdfs. Don't need /hdfs bit when using hadoop tools
# TODO: add in check as to whether the user wants it on hdfs or not...
######################
for f in $(find . -name "*.root")
do
    output=$(basename $f)
    hadoop fs -copyFromLocal $output ${outputDir///hdfs}/$output
done
