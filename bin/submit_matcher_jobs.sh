#!/bin/bash

# To submit lots of RunMatcher jobs
#
# Add list of L1Tree files to files list
# Change fdir to point at dir with L1Tree files (pairs output file will go there)
# Edit the output filename and if applying any corrections

declare -a files=(
L1Tree_QCDFlatPhys14BX50_GCT_QCDFlatPhys14_newRCTv2_calibrated.root
) 

fdir="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDFlatPhys14_newRCTv2_calibrated/"

# update the CMSSW area in the batch script
sed -i s@CMSSW_.*\/src@${CMSSW_VERSION}/src@g matcher_batch.sh

for f in "${files[@]}"
do
	jobname=${f#L1Tree_QCD_Pt-}
	jobname=${jobname%_Phys14_*.root}
	outname=${f#L1Tree_}
	outname=${outname%.root}
	echo "$outname"
	echo "$jobname"
	bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${fdir}/${f} -O ${fdir}/pairs_${outname}_GCT_ak5_ref14to1000_l10to500.root --l1Dir l1ExtraTreeProducer --l1Branches cenJet FwdJet TauJet"
done
