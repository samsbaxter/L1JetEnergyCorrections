#!/bin/bash

# Submit resolution jobs on HTCondor using the DAGman feature.
# All you need to do is add in the relevant pairs file(s) you wish to run over.
# Use absolute path!
#
# For each pairs file, creates a dag file. This does all the eta bins in
# separate jobs, and then hadds them all after.

declare -a pairsFiles=(
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_newRCTv2_calibrated_newLUT_3_Aug_15_Bristol/pairs_QCD_Pt-15to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_AVE20BX25_newRCTv2_calibrated_newLUT_3_Aug_15_Bristol_gtJets_ref14to1000_l10to500.root
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
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" resolution_condor.sh
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" hadd.sh

# make a copy of the condor script for these jobs. Can use the same one for
# all of them, just pass in different arguments
outfile="submit_resolution.condor"
cp submit_template.condor "$outfile"
echo 'arguments = $(opts)' >> "$outfile"
echo "queue" >> "$outfile"

# Replace correct parts
sed -i 's@SEDNAME@resolution/resolution@g' $outfile
sed -i 's/SEDEXE/resolution_condor.sh/g' $outfile
cdir=${PWD%HTCondor}
echo $cdir
sed -i "s@SEDINPUTFILES@$cdir/makeResolutionPlots.py, $cdir/binning.py, $PWD/condor_wrapper.py, $cdir/correction_LUT_plot.py, $cdir/common_utils.py@" $outfile

declare -a statusFileNames=()

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
    dagfile="resolution_${timestamp}_${rand}.dag"
    echo "# dag file for $pairs" >> $dagfile
    echo "# output will be $fdir" >> $dagfile

    # Store all jobs names and output fileNames for later
    declare -a jobNames=()
    declare -a outFileNames=()

    # Special appendix, if desired (e.g. if changing a param)
    append=""

    outname=${fname/pairs_/res_}
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

        jobname="res_${etamin}to${etamax}"
        jobname="res_${i}"
        jobNames+=($jobname)

        outRootName="${fdir}/${outname}_${i}${append}.root"
        outFileNames+=($outRootName)

        echo "JOB $jobname $outfile" >> "$dagfile"
        echo "VARS $jobname opts=\"python makeResolutionPlots.py ${pairs} ${outRootName} --excl --etaInd ${i}\"" >> "$dagfile"
    done

    # Now do inclusive bins (central, forward, all)
    jobname="res_central"
    jobNames+=($jobname)
    outRootName="${fdir}/${outname}_central${append}.root"
    outFileNames+=($outRootName)
    echo "JOB $jobname $outfile" >> "$dagfile"
    echo "VARS $jobname opts=\"python makeResolutionPlots.py ${pairs} ${outRootName} --incl --central\"" >> "$dagfile"

    jobname="res_forward"
    jobNames+=($jobname)
    outRootName="${fdir}/${outname}_forward${append}.root"
    outFileNames+=($outRootName)
    echo "JOB $jobname $outfile" >> "$dagfile"
    echo "VARS $jobname opts=\"python makeResolutionPlots.py ${pairs} ${outRootName} --incl --forward\"" >> "$dagfile"

    jobname="res_all"
    jobNames+=($jobname)
    outRootName="${fdir}/${outname}_all${append}.root"
    outFileNames+=($outRootName)
    echo "JOB $jobname $outfile" >> "$dagfile"
    echo "VARS $jobname opts=\"python makeResolutionPlots.py ${pairs} ${outRootName} --incl\"" >> "$dagfile"

    # Now add job for hadding
    finalRootName="${fdir}/${outname}${append}.root"
    haddJobName="haddResolution"
    echo "JOB $haddJobName hadd.condor" >> "$dagfile"
    echo "VARS $haddJobName opts=\"$finalRootName ${outFileNames[@]}\"" >> "$dagfile"

    # Add in parent-child relationships & status file
    echo "PARENT ${jobNames[@]} CHILD $haddJobName" >> "$dagfile"
    statusfile="resolution_${timestamp}_${rand}.status"
    echo "NODE_STATUS_FILE $statusfile 30" >> "$dagfile"
    statusFileNames+=($statusfile)

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

if [ ${#statusFileNames[@]} -gt "1" ]; then
    echo "To check all statuses:"
    echo "./DAGstatus.py ${statusFileNames[@]}"
fi