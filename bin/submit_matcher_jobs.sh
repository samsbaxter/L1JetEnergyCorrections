#!/bin/bash

# To submit lots of RunMatcher jobs
#
# Add list of L1Tree files to files list - make sure you use the FULL filepath

declare -a files=(
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-300to470_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-600to800_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
/afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-800to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
) 

# update the CMSSW area in the batch script
sed -i s@CMSSW_.*\/src@${CMSSW_VERSION}/src@g matcher_batch.sh

for f in "${files[@]}"
do
    fdir=$(dirname $f)
    filename=$(basename $f)
	jobname=${filename#L1Tree_}
	jobname=${jobname%.root}
	outname=${filename#L1Tree_}
	outname=${outname%.root}
    echo "$fdir"
    echo "${outname}"
    echo "Jobname: $jobname"
    bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_preGt_ak5_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk5 --l1Dir l1ExtraTreeProducerIntern"  # stage1 preGt, ak5
    bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_preGt_ak4_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern"  # stage1 preGt, ak4
    # bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_GCT_ak5_ref14to1000_l10to500.root --l1Dir l1ExtraTreeProducer --l1Branches cenJet tauJet fwdJet" # gct jets, ak5
    # bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_GCT_ak4_ref14to1000_l10to500.root --l1Dir l1ExtraTreeProducer --l1Branches cenJet tauJet fwdJet --refDir l1ExtraTreeProducerGenAk4"  # gct jets, ak4
    # bsub -q 8nh -J $jobname "sh matcher_batch.sh -I ${f} -O ${fdir}/pairs_${outname}_GCTintern_ak5_ref14to1000_l10to1000.root"  # gct internal jets, ak5
    # bsub -q 8nh -J $jobname "sh matcher_batch_data.sh -I ${f} -O ${fdir}/pairs_${outname}_ref0to1000.root " # data (ignores --l1Dir and --refDir)
done
