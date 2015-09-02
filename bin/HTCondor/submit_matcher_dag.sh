#!/bin/bash

# Submit resolution jobs on HTCondor using the DAGman feature.
# All you need to do is add in the relevant pairs file(s) you wish to run over.
# Use absolute path!
#
# For each pairs file, creates a dag file. This does all the eta bins in
# separate jobs, and then hadds them all after.

declare -a treeDirs=(
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-120to170_Spring15_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-15to30_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-170to300_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-300to470_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-30to50_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-470to600_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-50to80_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-600to800_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-800to1000_Spring15_AVE20BX25
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed0p5/QCD_Pt-80to120_Spring15_AVE20BX25
)

# update the setup scripts for worker nodes
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" condor_worker.sh
sed -i "s@RDIR=/.*@RDIR=$ROOTSYS@" condor_worker.sh
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" hadd.sh

# make a copy of the condor script for these jobs. Can use the same one for
# all of them, just pass in different arguments
outfile="submit_matcher.condor"
cp submit_template.condor "$outfile"
echo 'arguments = $(opts)' >> "$outfile"
echo "queue" >> "$outfile"

# Replace correct parts
sed -i 's@SEDNAME@matcher/matcher@g' $outfile
sed -i 's/SEDEXE/condor_worker.sh/g' $outfile
cdir=${PWD%HTCondor}
# echo $cdir

exe='RunMatcher' # FOR MC
# exe='RunMatcherData' # FOR DATA using l1Extra + reco jet
exePath=`which $exe`
sed -i "s@SEDINPUTFILES@$exePath@" $outfile

declare -a statusFileNames=()

# Queue up jobs
for dir in "${treeDirs[@]}"
do
    # Make DAG file for this directory file
    # To make sure we don't overlap with another, we give it a timestamp + random string
    timestamp=$(date "+%H%M%S")
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 3 | head -n 1)
    dagfile="pairs_${timestamp}_${rand}.dag"
    echo "# dag file for $dir" >> $dagfile
    echo "# output will be $dir" >> $dagfile

    # Store all jobs names and output fileNames for later
    declare -a jobNames=()
    declare -a outFileNames=()

    deltaR=0.7
    refMin=14

    # Special appendix, if desired (e.g. if changing a param)
    append="_preGt_ak4_ref${refMin}to1000_l10to500_dr${deltaR/./p}"

    # Add a matcher job for each L1Ntuple
    counter=0
    for tree in $dir/L1*.root
    do
        fdir=`dirname $tree`
        fname=`basename $tree`

        # echo "Using tree file $tree"

        outname=${fname/L1Tree_/pairs_}
        outname=${outname%.root}

        jobname="pairs$counter"
        jobNames+=($jobname)
        outRootName="${fdir}/${outname}${append}.root"
        outFileNames+=($outRootName)
        echo "JOB $jobname $outfile" >> "$dagfile"
        echo "VARS $jobname opts=\"${tree} ${outRootName} ${exe} -I ${tree} -O ${outRootName} --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern --l1Branches cenJet --refBranches cenJet --draw 0 --deltaR ${deltaR} --refMinPt ${refMin}\"" >> "$dagfile"
        ((counter++))
    done

    # Now add job(s) for hadding
    # This is a huge pain in the arse, since there's maximum number of parent
    # jobs a DAG will accept (or is it hadd's fault?)
    # Either way, we have to split it up into groups, and then hadd each group
    groupSize=200
    nJobs=${#outFileNames[@]}
    nInterHaddJobs=$((($nJobs+$groupSize+1)/$groupSize)) # ceiling
    modulus=$(($nJobs%$groupSize)) # modulus
    # floor=$(($nJobs/$groupSize)) # floor
    # Here we adjust the group size if the last job would just be hadding 1 file
    if [ "$modulus" -eq  "1" ]; then
        groupSize=199
        nInterHaddJobs=$((($nJobs+$groupSize+1)/$groupSize)) # ceiling
        # floor=$(($nJobs/$groupSize)) # floor
        # modulus=$(($nJobs%$groupSize)) # modulus
    fi

    # Either just do 1 hadd job, or a layer of intermediate hadding jobs
    if [ "$nInterHaddJobs" -eq 1 ]; then
        # Only 1 hadd job, proceed as usual
        outname=${outname%_*}
        outname=${outname/pairs_/pairs_$(basename $dir)_}
        finalRootName="$(dirname $dir)/pairs/${outname}${append}.root"
        echo "Final file:" $finalRootName
        haddJobName="hadder"
        echo "JOB $haddJobName hadd.condor" >> "$dagfile"
        echo "VARS $haddJobName opts=\"$finalRootName ${outFileNames[@]}\"" >> "$dagfile"
        # Add in parent-child relationships
        echo "PARENT ${jobNames[@]} CHILD $haddJobName" >> "$dagfile"
    else
        # An intermediate layer of hadd jobs
        declare -a interHaddJobNames=() # store intermediate hadd job names
        declare -a interHaddFileNames=() # store intermediate hadd output files
        i=0
        while [ "$i" -lt "$nInterHaddJobs" ]; do
            # collect all the info for this job: input files, output file, job names
            tmpOutput="$(dirname $dir)/pairs/${outname}${append}_inter$i.root"
            interHaddFileNames+=($tmpOutput)
            declare -a tmpInputFiles=()
            declare -a tmpJobParentNames=()
            lim=$(( ($i+1) * $groupSize ))
            if [ "$i" -eq "$((nInterHaddJobs-1))" ];
            then
                lim=$nJobs
            fi

            for ((j=(($i*$groupSize)); j<$lim; j++)); do
                tmpInputFiles+=(${outFileNames[$j]})
                tmpJobParentNames+=(${jobNames[$j]})
            done

            # add a job to DAG
            haddJobName="hadderInter${i}"
            interHaddJobNames+=($haddJobName)
            echo "JOB $haddJobName hadd.condor" >> "$dagfile"
            echo "VARS $haddJobName opts=\"$tmpOutput ${tmpInputFiles[@]}\"" >> "$dagfile"

            # Add in parent-child relationships
            echo "PARENT ${tmpJobParentNames[@]} CHILD $haddJobName" >> "$dagfile"
            (( i += 1 ))
        done
        # And now the final hadd job
        outname=${outname%_*}
        outname=${outname/pairs_/pairs_$(basename $dir)_}
        finalRootName="$(dirname $dir)/pairs/${outname}${append}.root"
        echo "Final file:" $finalRootName
        haddJobName="haddFinal"
        echo "JOB $haddJobName hadd.condor" >> "$dagfile"
        echo "VARS $haddJobName opts=\"$finalRootName ${interHaddFileNames[@]}\"" >> "$dagfile"
        # Add in parent-child relationships
        echo "PARENT ${interHaddJobNames[@]} CHILD $haddJobName" >> "$dagfile"
    fi

    # Add in status file
    statusfile="pairs_${timestamp}_${rand}.status"
    echo "NODE_STATUS_FILE $statusfile 30" >> "$dagfile"
    statusFileNames+=($statusfile)

    autoSub=true
    for f in "${outFileNames[@]}"; do
        if [ -e $f ]; then
            echo "One of the individual output files already exists"
            autoSub=false
            break
        fi
    done
    if [ -e $finalRootName ]; then
        echo "Final output file already exists"
        autoSub=false
    fi
    echo ""
    echo "Condor DAG script made"
    echo "Submit with:"
    echo "condor_submit_dag $dagfile"
    if [ $autoSub = true ]; then
        echo "Submitting..."
        condor_submit_dag "$dagfile"
    else
        echo "Not auto submitting as output file(s) already exists. Check your job description file is OK first!"
    fi
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