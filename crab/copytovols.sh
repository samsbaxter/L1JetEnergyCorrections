#!/bin/bash/
for NUM in {370..572}; do
srmcp srm://gfe02.grid.hep.ph.ic.ac.uk:8443/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/sabaxter/JetHT/crab_JetHT_Run2016G-07Aug17-v1_AOD_RecoRAW_JetHTReReco_280015_HF_L1JEC_13022017_ICL/180213_160643/0000/L1Ntuple_${NUM}.root file://///vols/cms/ssb216/L1Ntuplespf/ -streams_num=1
#/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/sabaxter/JetHT/crab_JetHT_Run2016G-07Aug17-v1_AOD_RecoRAW_JetHTReReco_280015_HF_L1JEC_05022017_ICL/180205_153514/0000/L1Ntuple_${NUM}.root file://///vols/cms/ssb216/L1Ntuplespf/ -streams_num=1
done

