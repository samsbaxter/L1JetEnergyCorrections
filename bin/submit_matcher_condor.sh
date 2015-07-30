#!/bin/bash

# To submit lots of RunMatcher jobs on HTCondor
#
# Add list of L1Tree files to files list - make sure you use the FULL filepath

declare -a files=(
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-30to50_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-170to300_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
# /hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/L1Tree_QCD_Pt-80to120_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Collisions/Stage1_50ns/251718_HLTPhysics1/L1Tree_251718_HLTPhysics1.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Collisions/Stage1_50ns/251718_HLTPhysics2/L1Tree_251718_HLTPhysics2.root
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Collisions/Stage1_50ns/251718_HLTPhysics3/L1Tree_251718_HLTPhysics3.root
) 

# make a copy of the condor script
outfile="submit_matcher.condor"
cp submit_template.condor "$outfile"

# put the right exe in there
exe=`which RunMatcher`
exe=`which RunMatcherDataStage1GT`
echo $exe
sed -i "s@SEDINPUTFILES@$exe@" "$outfile"
sed -i "s@SEDEXE@$PWD/matcher_condor.py@" "$outfile"
sed -i "s@SEDNAME@matcher@" "$outfile"

# now queue up jobs
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
    # echo "arguments=RunMatcher -I $f -O ${fdir}/pairs_${outname}_preGt_ak5_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk5 --l1Dir l1ExtraTreeProducerIntern" >> "$outfile"
    # echo "queue" >> "$outfile"
    # echo "arguments=RunMatcher -I $f -O ${fdir}/pairs_${outname}_preGt_ak4_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern" >> "$outfile"
    # echo "queue" >> "$outfile"
    echo "arguments=RunMatcherDataStage1GT -I $f -O ${fdir}/pairs_${outname}_Stage1_50ns_ref14to1000_l10to500_v2.root" >> "$outfile"
    echo "queue" >> "$outfile"
done
echo ""
echo "Condor script made"
echo "Submitting:"
# condor_submit $outfile
echo "Submit with:"
echo "condor_submit $outfile"
