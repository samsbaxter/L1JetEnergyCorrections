#!/bin/bash

# Submit calibration jobs on HTCondor using the DAGman feature.
# All you need to do is add in the relevant pairs file(s) you wish to run over.
# Use absolute path!
#
# For each pairs file, creates a dag file. This does all the eta bins in
# separate jobs, and then hadds them all after.

declare -a pairsFiles=(
# /hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/pairs/pairs_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_Run260627/pairs/pairs_ntuples_data_ref10to5000_l10to5000_dr0p4.root
)

declare -a etaBins=(
0.0
0.348
0.695
1.044
1.392
1.74
2.172
3.0
# 3.5
# 4.0
# 4.5
# 5
)

# update the setup scripts for worker nodes
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" condor_worker.sh
sed -i "s@RDIR=/.*@RDIR=$ROOTSYS@" condor_worker.sh
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" hadd.sh

# make a copy of the condor script for these jobs. Can use the same one for
# all of them, just pass in different arguments
outfile="submit_calibration.condor"
cp submit_template.condor "$outfile"
echo 'arguments = $(opts)' >> "$outfile"
echo "queue" >> "$outfile"

# Replace correct parts
datestamp=$(date "+%d_%b_%Y")
logDir="jobs/calibration/${datestamp}"
if [ ! -d "$logD" ]; then
    mkdir -p $logDir
fi
sed -i "s@SEDNAME@${logDir}/calibration@g" $outfile # for log files
sed -i 's/SEDEXE/condor_worker.sh/g' $outfile # thing to execute on worker node
cdir=${PWD%HTCondor}
echo $cdir
sed -i "s@SEDINPUTFILES@$cdir/runCalibration.py, $cdir/binning.py, $cdir/correction_LUT_plot.py, $cdir/common_utils.py@" $outfile

declare -a statusFileNames=()

# Loop over PU ranges for PU10to30 sample:
# declare -a puMins=(
#     0
#     15
#     30
# )
# declare -a puMaxs=(
#     10
#     25
#     40
# )

# Or for 0PU:
declare -a puMins=(
    -100
)
declare -a puMaxs=(
    100
)


# loop over the two arrays pairwise
for((p=0; p<${#puMins[@]}; ++p)); do
    puMin=${puMins[p]}
    puMax=${puMaxs[p]}

    # Special appendix, if desired (e.g. if changing a param)
    append=""  # 0PU
    # append="_PU${puMin}to${puMax}"  # PU binned

    # Queue up jobs
    for pairs in "${pairsFiles[@]}"
    do
        # check file actually exists
        if [ ! -e "$pairs" ]; then
            echo "$Pairs does not exist!"
            exit 1
        fi

        # Puts the output in relevant directory,
        # e.g. if pairs in Stage1/pairs/xxx/pairs.root
        # output goes to Stage1/output/xxx/output.root
        fdir=`dirname $pairs`
        fdir=${fdir/pairs/output}
        if [ ! -d "$fdir" ]; then
            mkdir -p $fdir
            echo "Making output dir $fdir"
        fi
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

            fwdOpt=""
            if [[ "$etamin" > 2.9 ]]; then
                fwdOpt="--no-correction-fit"
            fi
            echo "JOB $jobname $outfile" >> "$dagfile"
            echo "VARS $jobname opts=\"${pairs} ${outRootName} python runCalibration.py ${pairs} ${outRootName} --no-genjet-plots ${fwdOpt} --stage2 --PUmin ${puMin} --PUmax ${puMax} --etaInd ${i}\"" >> "$dagfile"
        done

        # Now add job for hadding
        finalRootName="${fdir}/${outname}${append}.root"
        haddJobName="haddCalib"
        echo "JOB $haddJobName hadd_small.condor" >> "$dagfile"
        echo "VARS $haddJobName opts=\"$finalRootName ${outFileNames[@]}\"" >> "$dagfile"
        echo "Output file: $finalRootName"

        # Add in parent-child relationships & status file
        echo "PARENT ${jobNames[@]} CHILD $haddJobName" >> "$dagfile"
        statusfile="calibration_${timestamp}_${rand}.status"
        echo "NODE_STATUS_FILE $statusfile 30" >> "$dagfile"
        statusFileNames+=($statusfile)

        # Submit jobs
        autoSub=true
        for f in "${outFileNames[@]}"; do
            if [ -e $f ]; then
                autoSub=false
                break
            fi
        done
        echo ""
        echo "Condor DAG script made"
        echo "Submit with:"
        echo "condor_submit_dag $dagfile"
        if [ $autoSub = true ]; then
            echo "Submitting..."
            condor_submit_dag "$dagfile"
        else
            echo "***** WARNING: Not auto submitting. *****"
        fi
        echo ""
        echo "Check status with:"
        echo "./DAGstatus.py $statusfile"
        echo ""
        echo "(may take a little time to appear)"
    done
done

if [ ${#statusFileNames[@]} -gt "1" ]; then
    echo "To check all statuses:"
    echo "./DAGstatus.py ${statusFileNames[@]}"
fi