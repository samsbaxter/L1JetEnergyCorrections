#!/bin/bash

# Submit matcher jobs on HTCondor using the DAGman feature.
# All you need to do is add in the relevant directories of L1Ntuple files you wish to run over.
# Use absolute path!
#
# For each directory, this will create a DAG file will all the necessary job and submit it.
# It will make a pairs file for each L1Ntuple file, in the same directory as the L1Ntuple file.
# It will then hadd all the pairs files from that directory,
# and put them in the parent directory of the Ntuple directory, in a subdirectory called "pairs".

declare -a treeDirs=(
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDFlatSpring15BX25HCALFix_stage1HFfix_PU15to25_rctv4_jetSeed5/QCDFlatSpring15BX25FlatNoPUHCALFix
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
    # append="_preGt_ak4_ref${refMin}to1000_l10to500_dr${deltaR/./p}"
    append="_GT_ak4_ref${refMin}to1000_l10to500_dr${deltaR/./p}"

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
        outRootPath="${fdir}/${outname}${append}.root"
        outFileNames+=($outRootPath)
        echo "JOB $jobname $outfile" >> "$dagfile"
        # For jets sent to GT
        echo "VARS $jobname opts=\"${tree} ${outRootPath} ${exe} -I ${tree} -O ${outRootPath} --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducer --l1Branches cenJet fwdJet --refBranches cenJet --draw 0 --deltaR ${deltaR} --refMinPt ${refMin}\"" >> "$dagfile"
        # For internal jets:
        # echo "VARS $jobname opts=\"${tree} ${outRootPath} ${exe} -I ${tree} -O ${outRootPath} --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern --l1Branches cenJet --refBranches cenJet --draw 0 --deltaR ${deltaR} --refMinPt ${refMin}\"" >> "$dagfile"
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
    # Here we adjust the group size if the last job would just be hadding 1 file
    if [ "$modulus" -eq  "1" ]; then
        groupSize=199
        nInterHaddJobs=$((($nJobs+$groupSize+1)/$groupSize)) # ceiling
    fi

    # Output directory for final hadded pairs file
    pairsDirectory=$(dirname $dir)/pairs
    # Check if directory exists, if not make it
    if [ ! -e "$pairsDirectory" ]; then
        echo "Making $pairsDirectory"
        mkdir -p "$pairsDirectory"
    fi

    # Either just do 1 hadd job, or a layer of intermediate hadding jobs
    if [ "$nInterHaddJobs" -eq 1 ]; then
        # Only 1 hadd job, proceed as usual
        outname=${outname%_*} # chop off the number (e.g. _99)
        outname=${outname/pairs_/pairs_$(basename $dir)_} # add in the dataset directory
        finalRootPath="${pairsDirectory}/${outname}${append}.root"
        echo "Final file: $finalRootPath"
        haddJobName="haddFinal"
        echo "JOB $haddJobName hadd.condor" >> "$dagfile"
        echo "VARS $haddJobName opts=\"$finalRootPath ${outFileNames[@]}\"" >> "$dagfile"
        # Add in parent-child relationships
        echo "PARENT ${jobNames[@]} CHILD $haddJobName" >> "$dagfile"
    else
        # An intermediate layer of hadd jobs
        declare -a interHaddJobNames=() # store intermediate hadd job names
        declare -a interHaddFileNames=() # store intermediate hadd output files
        i=0
        while [ "$i" -lt "$nInterHaddJobs" ]; do
            # collect all the info for this job: input files, output file, job names
            rand=$(cat /dev/urandom | tr -cd [:alnum:] | head -c 3)
            tmpOutput="${pairsDirectory}/${outname}${append}_inter${i}_${timestamp}_${rand}.root"
            interHaddFileNames+=($tmpOutput)
            declare -a tmpInputFiles=()
            declare -a tmpJobParentNames=()
            lim=$(( ($i+1) * $groupSize ))
            if [ "$i" -eq "$((nInterHaddJobs-1))" ]; then
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
        outname=${outname%_*} # chop off the number (e.g. _99)
        outname=${outname/pairs_/pairs_$(basename $dir)_} # add in the dataset directory
        finalRootPath="${pairsDirectory}/${outname}${append}.root"
        echo "Final file: $finalRootPath"
        haddJobName="haddFinal"
        echo "JOB $haddJobName hadd.condor" >> "$dagfile"
        echo "VARS $haddJobName opts=\"$finalRootPath ${interHaddFileNames[@]}\"" >> "$dagfile"
        # Add in parent-child relationships
        echo "PARENT ${interHaddJobNames[@]} CHILD $haddJobName" >> "$dagfile"
    fi

    # Add in status file
    statusfile="pairs_${timestamp}_${rand}.status"
    echo "NODE_STATUS_FILE $statusfile 30" >> "$dagfile"
    statusFileNames+=($statusfile)

    # Submit, but check if it will overwrite anything
    autoSub=true
    for f in "${outFileNames[@]}"; do
        if [ -e "$f" ]; then
            echo "One of the individual output files already exists"
            autoSub=false
            break
        fi
    done
    if [ -e "$finalRootPath" ]; then
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
        echo "Not auto submitting."
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