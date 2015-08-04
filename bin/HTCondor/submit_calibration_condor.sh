#!/bin/bash

# submit calibration jobs on HTCondor. For each job, does 1 eta bin for 1 pairs file.
# all you should change is pairsFile(s) array

declare -a pairsFiles=(
# "/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDPhys14_newRCTv2/pairs_QCD_Pt-15to600_Phys14_AVE30BX50_GCT_QCDPhys14_newRCTv2_GCT_ak5_ref14to1000_l10to500.root"
"/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/TTbarSpring15_GCT_newRCTv2_newGCT/pairs_TTbarSpring15AVE30BX50_TTbarSpring15_GCT_newRCTv2_newGCT_GCT_ak5_ref14to1000_l10to500.root"
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

# update the setup script on worker side
sed -i "s/VER=CMSSW_.*/VER=$CMSSW_VERSION/" calibration_condor.sh

# make a copy of the condor script
outfile="submit_calibration.condor"
cp submit_template.condor "$outfile"

cdir=${PWD%HTCondor}
echo $cdir

# Replace correct parts
sed -i 's/SEDNAME/calibration/g' $outfile
sed -i 's/SEDEXE/calibration_condor.sh/g' $outfile
sed -i "s@SEDINPUTFILES@$cdir/runCalibration.py, $cdir/binning.py, $cdir/condor_wrapper.py, $cdir/correction_LUT_plot.py, $cdir/common_utils.py@" $outfile

# Queue up jobs
for pairs in "${pairsFiles[@]}"
do
    fdir=`dirname $pairs`
    fname=`basename $pairs`

    echo "Using pairs file $pairs"
    echo "Writing output to directory: $fdir"

    len=${#etaBins[@]}
    len=$(( len - 1 ))
    for ((i=0;i<$len;++i));
    do
        j=$(( i + 1 ))
        etamin=${etaBins[i]}
        etamax=${etaBins[j]}
        jobname="${etamin}to${etamax}"
        outname=${fname#pairs_}
        outname=${outname%.root}
        outname="output_${outname}_${i}.root"
        echo "$jobname"
        echo "$outname"
        echo "arguments = python runCalibration.py --no_genjet_plots ${fdir}/${fname} ${fdir}/${outname} --etaInd ${i}" >> "$outfile"
        echo "queue" >> "$outfile"
    done
done

echo ""
echo "Condor script made"
echo "Submitting:"
# condor_submit $outfile
echo "Submit with:"
echo "condor_submit $outfile"
