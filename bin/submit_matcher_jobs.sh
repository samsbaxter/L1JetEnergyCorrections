#!/bin/bash

# To submit lots of RunMatcher jobs
#
# Add list of L1Tree files to files list
# Change fdir to point at dir with L1Tree files (pairs output file will go there)
# Edit the output filename and if applying any corrections

declare -a files=(
L1Tree_QCD_Pt-120to170_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-15to30_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-170to300_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-300to470_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-30to50_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-470to600_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-50to80_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-600to800_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-800to1000_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
L1Tree_QCD_Pt-80to120_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_HCALhack_v2.root
) 

fdir="/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_2_0/src/L1Trigger/L1JetEnergyCorrections/QCD_Phys14_AVE30BX50_newRCT_HCALhack_v2/"

for f in "${files[@]}"
do
	jobname=${f#L1Tree_QCD_Pt-}
	jobname=${jobname%_Phys14_*.root}
	outname=${f#L1Tree_}
	outname=${outname%.root}
	echo "$outname"
	echo "$jobname"
	bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${fdir}/${f} -O ${fdir}/pairs_${outname}_GCT_ak5_ref14to1000_l10to500.root"
done
