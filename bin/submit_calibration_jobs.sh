#!/bin/bash

# To submit lots of runCalibration jobs on lxbatch system (or any bsub)
# Splits it up by eta bin
#
# Change pairs variable to full path of pairs file you want to run over
# The output files from runCalibration.py will be made in the same directory


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
5.001
) 

pairs="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0/src/L1Trigger/L1JetEnergyCorrections/QCD_Phys14_AVE30BX50_newRCT_HCALhack_v2/pairs_QCD_Pt-15to1000_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2_GCT_ak5_ref14to1000_l10to500.root"

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
    bsub -q 8nh -J $jobname "sh calibration_batch.sh --no_genjet_plots ${fdir}/${fname} ${fdir}/${outname} --etaInd ${i}"
done