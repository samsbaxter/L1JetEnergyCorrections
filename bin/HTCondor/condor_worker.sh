#!/bin/bash -e
#
# This script is designed to run the command on the condor worker node.
# It solves 2 issues:
#
# 1) it's best to copy the input file from /hdfs to the local worker node.
# This avoids several processes trying to access the same file simultaneously
# (which is mayhem in ROOT).
#
# 2) you cannot stream the outut to /hdfs. Instead we write to a local file and
# then copy it across afterwards.
#
# This script does both seamlessly so the user can issue the normal command and
# not worry about moving files around.
# It will run the command, move the output back to /hdfs, and clean up.

inputFile="$1"
shift
outputFile="$1"
shift
commandArr="$@"
commands=${commandArr[@]}
echo "Input file: $inputFile"
echo "Output file: $outputFile"
echo "Commands: $commands"
exe="$1"

# sandbox our work, to avoid it being transferred over afterwards
mkdir scratch

# setup CMSSW for ROOT
# VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
# . $VO_CMS_SW_DIR/cmsset_default.sh
# VER=CMSSW_7_6_0_pre7
# if [ ! -d $VER ];
# then
#     scramv1 project CMSSW $VER
# fi
# cd $VER/src/
# eval `scramv1 runtime -sh`
# cd ../..
# ls
# export PATH=$PWD:$PATH
# ls -l /cvmfs/cms.cern.ch/slc6_amd64_gcc491/lcg/root/6.02.00-odfocd2/etc

RDIR=/cvmfs/cms.cern.ch/slc6_amd64_gcc493/lcg/root/6.02.12-kpegke2/
source $RDIR/bin/thisroot.sh

# generate new temporary unique filename
# rand=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 3 | head -n 1)  # don't use this, as can hang
rand=$(date +%s%N)
newOutput="scratch/tmp_${rand}.root"
newInput="scratch/$(basename $inputFile)"
echo "New input arg: $newInput"
echo "New output arg: $newOutput"

# copy across exe
exeBasename=$(basename $exe)
hadoop fs -copyToLocal "${exe#/hdfs}" "$exeBasename"
commands=${commands/$exe/$exeBasename}
chmod u+x "$exeBasename"

# copy across inputfile
# hadoop fs -copyToLocal "${inputFile#/hdfs}" "$newInput"
# commands=${commands/$inputFile/$newInput}
# echo $PWD
# ls -l

# setup new locations in users commands
commands=${commands/$outputFile/$newOutput}
echo "New commands:"
echo "$commands"

# run commands
eval $commands

result=$?

if [[ "$result" -ne 0 ]]; then
    cleanup
    exit $result
fi


# copy result across
hadoop fs -copyFromLocal -f "$newOutput" "${outputFile#/hdfs}"

# tidy up
function cleanup {
    find . -name "*.root" -delete
    find . -name "*.pyc" -delete
    find . -name "scratch" -delete
    rm RunMatcher*
    find . -name "$exeBasename" -delete
    # find . -name "$VER" -delete
}
trap cleanup EXIT