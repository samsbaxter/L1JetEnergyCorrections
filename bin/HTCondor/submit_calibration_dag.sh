#!/bin/bash

# Submit calibration jobs on HTCondor using the DAGman feature.
# All you need to do is add in the relevant pairs file(s) you wish to run over.
# Use absolute path!
#
# For each pairs file, creates a dag file. This does all the eta bins in
# separate jobs, and then hadds them all after.

declare -a pairsFiles=(
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/pairs_QCD_Pt-15to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2_preGt_ak4_ref14to1000_l10to500.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed5/pairs_QCD_Pt-15to170_300to1000_Spring15_AVE20BX25_Stage1_jetSeed5_MCRUN2_V9_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed5/pairs_QCD_Pt-15to30_Spring15_AVE20BX25_Stage1_jetSeed5_MCRUN2_V9_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_dr0p4.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed5/pairs_QCD_Pt-30to170_300to1000_Spring15_AVE20BX25_Stage1_jetSeed5_MCRUN2_V9_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500.root
)

declare -a etaBins=(
0
0.348
0.695
1.044
1.392
1.74
2.172
3.0
3.5
4.0
4.5
5
)

# update the setup scripts for worker nodes
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" calibration_condor.sh
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" hadd.sh

# make a copy of the condor script for these jobs. Can use the same one for
# all of them, just pass in different arguments
outfile="submit_calibration.condor"
cp submit_template.condor "$outfile"
echo 'arguments = $(opts)' >> "$outfile"
echo "queue" >> "$outfile"

# Replace correct parts
sed -i 's@SEDNAME@calibration/calibration@g' $outfile
sed -i 's/SEDEXE/calibration_condor.sh/g' $outfile
cdir=${PWD%HTCondor}
echo $cdir
sed -i "s@SEDINPUTFILES@$cdir/runCalibration.py, $cdir/binning.py, $PWD/condor_wrapper.py, $cdir/correction_LUT_plot.py, $cdir/common_utils.py@" $outfile

# Queue up jobs
for pairs in "${pairsFiles[@]}"
do
    fdir=`dirname $pairs`
    fname=`basename $pairs`

    echo "Using pairs file $pairs"
    echo "Writing output to directory: $fdir"

    # Make DAG file for this pairs file
    # To make sure we don't overlap with another, we give it a timestamp + random string
    timestamp=$(date "+%H%M%S")
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 3 | head -n 1)
    dagfile="calibration_${timestamp}_${rand}.dag"
    echo "# dag file for $pairs" >> $dagfile
    echo "# output will be $fdir" >> $dagfile

    # Store all jobs names and output fileNames for later
    declare -a jobNames=()
    declare -a outFileNames=()

    # Special appendix, if desired (e.g. if changing a param)
    append="_fitMin20"

    outname=${fname/pairs_/output_}
    outname=${outname%.root}

    # Write jobs to DAG file
    # Do individual eta bins first
    len=${#etaBins[@]}
    len=$(( len - 1 ))
    for ((i=0;i<$len;++i));
    do
        j=$(( i + 1 ))
        etamin=${etaBins[i]}
        etamax=${etaBins[j]}

        jobname="calib_${etamin}to${etamax}"
        jobname="calib_${i}"
        jobNames+=($jobname)

        outRootName="${fdir}/${outname}_${i}${append}.root"
        outFileNames+=($outRootName)

        echo "JOB $jobname $outfile" >> "$dagfile"
        echo "VARS $jobname opts=\"python runCalibration.py ${pairs} ${outRootName} --etaInd ${i}\"" >> "$dagfile"
    done

    # Now add job for hadding
    finalRootName="${fdir}/${outname}${append}.root"
    haddJobName="haddCalib"
    echo "JOB $haddJobName hadd.condor" >> "$dagfile"
    echo "VARS $haddJobName opts=\"$finalRootName ${outFileNames[@]}\"" >> "$dagfile"

    # Add in parent-child relationships & status file
    echo "PARENT ${jobNames[@]} CHILD $haddJobName" >> "$dagfile"
    statusfile="calib_${timestamp}_${rand}.status"
    echo "NODE_STATUS_FILE $statusfile 30" >> "$dagfile"

    echo ""
    echo "Condor DAG script made"
    echo "Submit with:"
    echo "condor_submit_dag $dagfile"
    echo "Submitting..."
    condor_submit_dag "$dagfile"
    echo ""
    echo "Check status with:"
    echo "./DAGstatus.py $statusfile"
    echo ""
    echo "(may take a little time to appear)"
done

