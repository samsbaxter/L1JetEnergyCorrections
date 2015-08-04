#!/bin/bash

# Store args
script=$1
dataset=$2
filesPerJob=$3
totalFiles=$4
outputDir=$5
ind=$6 # ind is the job number

# top level of worker node
worker="$PWD"
export HOME=$worker

# First setup CMSSW
cmssw_version=CMSSW_7_4_6_patch6
echo "Setting up ${cmssw_version} ..."
echo "... sourcing CMS default environment from CVMFS"
source /cvmfs/cms.cern.ch/cmsset_default.sh
echo "... creating CMSSW project area"
scramv1 project CMSSW ${cmssw_version}
cd ${cmssw_version}/src
eval `scramv1 runtime -sh`
echo "${cmssw_version} has been set up"

git config --global user.github "raggleton"
git config --global user.name "Robin Aggleton"
git config --global user.email "robin.aggleton@cern.ch"
git config -l
export CMSSW_GIT_REFERENCE="${worker}/.cmsgit-cache"

# Setup packages
# git cms-addpkg L1Trigger/L1TCalorimeter
git clone https://github.com/cms-l1-dpg/L1Ntuples.git L1TriggerDPG/L1Ntuples
git clone https://github.com/raggleton/L1JetEnergyCorrections.git L1Trigger/L1JetEnergyCorrections

xrootd="root://xrootd.unl.edu/"

# Make list of files
idx=$(($filesPerJob * $ind))
limit=$filesPerJob
if [ $((($ind + 1)*$filesPerJob)) -gt $totalFiles ]
    then
    limit=$(($totalFiles - ($ind * $filesPerJob) ))
fi
echo das_client.py --query="file dataset=$dataset" --limit $limit --idx $idx
# Loop over output for das_client.py, get files, write to a python file
pyfile="inputs.py"

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
# remove the last trailing ,
sed -i '$s@,$@@' $pyfile
echo "]" >> $pyfile

cat $pyfile

# Get Golden JSON
wget https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Cert_246908-251883_13TeV_PromptReco_Collisions15_JSON_v2.txt

# Move the cms config script from top level to pwd and build everything!
mv $worker/$script .
scram b -j9
ls

# Now finally run script!
cmsRun $script
echo "CMS JOB OUTPUT" $?

# Get output filename, make a new unique one
output=$(find . -name "L1Tree*.root" | xargs basename)
echo $output

output_file=${output/.root/_$ind.root}

# Copy across to hdfs. Don't need /hdfs bit
hadoop fs -copyFromLocal $output ${outputDir///hdfs}/$output_file
