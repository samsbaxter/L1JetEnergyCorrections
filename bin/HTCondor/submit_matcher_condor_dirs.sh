#!/bin/bash

# To submit lots of RunMatcher jobs on HTCondor
#
# Add list of L1Tree files to files list - make sure you use the FULL filepath

declare -a treeDirs=(
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-15to30_Phys14_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-30to50_Phys14_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-50to80_Phys14_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-80to120_Phys14_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-120to170_Phys14_AVE20BX25
/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_oldSetup/QCD_Pt-170to300_Phys14_AVE20BX25
)

# make a copy of the condor script
outfile="submit_matcher.condor"
cp submit_template.condor "$outfile"

# put the right exe in there
exe=`which RunMatcher` # FOR MC
# exe=`which RunMatcherData` # FOR DATA using l1Extra + reco jet
# exe=`which RunMatcherDataStage1GT` # FOR DATA where l1 stored in GT + reco jet
echo $exe
sed -i "s@SEDINPUTFILES@$exe@" "$outfile"
sed -i "s@SEDEXE@$PWD/matcher_condor.py@" "$outfile"
sed -i "s@SEDNAME@matcher@" "$outfile"

# now queue up jobs
for d in "${treeDirs[@]}"
do
    for f in $(ls $d/L1*.root)
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
        # echo "arguments=RunMatcher -I $f -O ${fdir}/pairs_${outname}_preGt_ak4_ref14to1000_l10to500.root --refDir l1ExtraTreeProducerGenAk4 --l1Dir l1ExtraTreeProducerIntern" >> "$outfile"
        # echo "arguments=RunMatcherDataStage1GT -I $f -O ${fdir}/pairs_${outname}_Stage1_50ns_ref14to1000_l10to500_v2.root" >> "$outfile"
        echo "arguments=RunMatcher -I $f -O ${fdir}/pairs_${outname}_gtJets_ref14to1000_l10to500.root --l1Dir l1ExtraTreeProducer --l1Branches cenJet fwdJet --refDir l1ExtraTreeProducerGenAk4 --refBranches cenJet" >> "$outfile"
        # echo "arguments=RunMatcherData -I $f -O ${fdir}/pairs_${outname}_preGtJets_reco_ref14to1000_l10to500.root" >> "$outfile"
        echo "queue" >> "$outfile"
    done
done
echo ""
echo "Condor script made"
echo "Submitting:"
# condor_submit $outfile
echo "Submit with:"
echo "condor_submit $outfile"
