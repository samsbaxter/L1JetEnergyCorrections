#!/bin/bash

# Manually copy output from crab jobs, from bristol to AFS
# Note this was a quick hack script, but may be useful in future if CRAB goes down,
# or you need to mannually copy over for whatever reason

declare -a folders=(
#QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-120to170_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170318/0000
#QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-15to30_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170400/0000
#QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-170to300_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170326/0000
#QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-300to470_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170236/0000
QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-30to50_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170310/0000
QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-470to600_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170257/0000
QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-50to80_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170247/0000
QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-600to800_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170334/0000
# QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-800to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170227/0000
QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/crab_QCD_Pt-80to120_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2/150625_170217/0000
)

for f in "${folders[@]}"
do
    qcdDir=$(echo $f | cut -d "/" -f1)
    crabDir=$(echo $f | cut -d "/" -f2)
    rootfile=${crabDir#crab_}
    echo $qcdDir
    echo $crabDir
    echo $rootfile
    gfal-copy -r gsiftp://lcgse01.phy.bris.ac.uk/dpm/phy.bris.ac.uk/home/cms/store/user/raggleto/${f} file:///afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_newRCTv2/${qcdDir}
    rm -r /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_newRCTv2/${qcdDir}/failed
    hadd /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_newRCTv2/L1Tree_${rootfile}.root /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_newRCTv2/${qcdDir}/*.root
    rm -r /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_newRCTv2/${qcdDir}
done
