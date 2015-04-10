#!/bin/bash

# To submit lots of runCalibration jobs

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

fdir="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0/src/L1Trigger/L1JetEnergyCorrections/QCD_Phys14_AVE30BX50/"
fname="pairs_QCD_Pt-80to120_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_GCT_ak5_ref14to1000_l10to500.root"

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
	echo "$outname"
	echo "$jobname"
	bsub -q 8nh -J $jobname "sh calibration_batch.sh --no_genjet_plots ${fdir}/${fname} ${fdir}/${outname} --etaInd ${i}"
done
