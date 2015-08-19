#!/bin/bash -e
# setup CMSSW for ROOT
VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
host=`hostname`
# some information for debugging
echo "I am running on $host"
echo "I got the following parameters: $@"
# source CMSSW env
. $VO_CMS_SW_DIR/cmsset_default.sh
# get CMSSW
VER=CMSSW_7_4_2
if [ ! -d $VER ];
then
    scramv1 project CMSSW $VER
fi
cd $VER/src/
eval `scramv1 runtime -sh`
cd ../..
ls
python condor_wrapper.py res $@