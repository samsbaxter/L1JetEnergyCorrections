#!/bin/bash

# To submit lots of RunMatcher jobs

declare -a files=(
L1Tree_QCD_Pt-30to50_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT.root
) 

fdir="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0/src/L1Trigger/L1JetEnergyCorrections/QCD_Phys14_AVE30BX50/"

for f in "${files[@]}"
do
	jobname=${f#L1Tree_QCD_Pt-}
	jobname=${jobname%_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT.root}
	outname=${f#L1Tree_}
	outname=${outname%.root}
	echo "$outname"
	echo "$jobname"
	bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${fdir}/${f} -O pairs_${outname}_GCT_ak5_ref14to1000_l10to500.root"
done
