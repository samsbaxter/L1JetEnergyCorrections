#!/bin/bash/
for NUM in {464..483}; do
srmcp srm://gfe02.grid.hep.ph.ic.ac.uk:8443/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/sabaxter/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/crab_qcdSummer17FlatPU28to62genSimRaw_qcdSummer17_genEmu_31Oct2017_928v96p49_noJEC/171031_114651/0000/L1Ntuple_${NUM}.root file://///vols/cms/ssb216/ -streams_num=1
done

