#!/bin/bash

# To submit lots of RunMatcher jobs
#
# Add list of L1Tree files to files list - make sure you use the FULL filepath

declare -a files=(
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/TTbarSpring15_GCT_oldRCT_oldGCT/L1Tree_TTbarSpring15AVE30BX50_TTbarSpring15_GCT_oldRCT_oldGCT.root
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/TTbarSpring15_GCT_newRCTv2_newGCT/L1Tree_TTbarSpring15AVE30BX50_TTbarSpring15_GCT_newRCTv2_newGCT.root
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/TTbarSpring15_GCT_newRCTv2_oldGCT/L1Tree_TTbarSpring15AVE30BX50_TTbarSpring15_GCT_newRCTv2_oldGCT.root
) 

# update the CMSSW area in the batch script
sed -i s@CMSSW_.*\/src@${CMSSW_VERSION}/src@g matcher_batch.sh

for f in "${files[@]}"
do
    fdir=$(dirname $f)
    filename=$(basename $f)
	jobname=${filename#L1Tree_}
	jobname=${jobname%_Spring15_*.root}
	outname=${filename#L1Tree_}
	outname=${outname%.root}
	echo "$outname"
	echo "$jobname"
    # bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${fdir}/${f} -O ${fdir}/pairs_${outname}_preGt_ak4_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern"
    # bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${fdir}/${f} -O ${fdir}/pairs_${outname}_preGt_ak5_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk5 --l1Dir l1ExtraTreeProducerIntern"
    bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_GCT_ak5_ref14to1000_l10to500.root --l1Dir l1ExtraTreeProducer --l1Branches cenJet tauJet fwdJet"
	bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_GCTintern_ak5_ref14to1000_l10to500.root"
done
