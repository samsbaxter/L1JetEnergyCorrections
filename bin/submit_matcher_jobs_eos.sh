#!/bin/bash -e

# To submit lots of RunMatcher jobs on files from EOS
#
# Add list of EOS directories files to files list, you don't need the root://eoscms.cern.ch bit
#
# Also make sure you pick the right executable to run!

# Output directory - set me
outDir="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Collisions/Stage1_50ns/"

# EOS directories - set me
declare -a eosDirs=(
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics1/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics2/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics3/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics4/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics5/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics6/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics7/
/eos/cms/store/group/dpg_trigger/comm_trigger/L1Trigger/Data/Collisions/251718_HLTPhysics8/
)

# Update CMSSW version in batch script
sed -i s@CMSSW_.*\/src@${CMSSW_VERSION}/src@g matcher_batch_data_stage1.sh

eosStem="root://eoscms.cern.ch/"
for d in "${eosDirs[@]}"
do
    for f in $(/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select ls $d)
    do
        file="$eosStem$d/$f"
        outname=${f#L1Tree_}
        outname=${outname%.root}
        fileDir=$(basename $d)
        outputDir="$outDir/$fileDir"
        if [ ! -d $outputDir ]
            then
            mkdir $outputDir
            echo "Making $outputDir"
        fi

        echo "Input: $file"
        echo "Output: ${outputDir}/pairs_${outname}"
        jobname="${fileDir}_${f%.root}"
        echo "Jobname: $jobname"
        # echo "sh matcher_batch_data_stage1.sh -I ${file} -O ${outputDir}/pairs_${outname}_ref14to1000.root "
        bsub -q 8nh -J $jobname "sh matcher_batch_data_stage1.sh -I ${file} -O ${outputDir}/pairs_${outname}_ref14to1000.root" # data (ignores --l1Dir and --refDir)
    done
done
