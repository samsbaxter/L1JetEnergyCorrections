#!/bin/bash
# run with qsub -q hep.q -l h_rt=1:0:0 -m bea -M samuel.baxter@desy.de -t 1-483:1 "matcher_batch_stage2l1gen.sh"
INPUT=/vols/cms/ssb216//L1Ntuples/L1Ntuple_${SGE_TASK_ID}.root

OUTPUT=/vols/cms/ssb216/matchedFiles/pairs_${SGE_TASK_ID}.root

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc530
cd /home/hep/ssb216/CMSSW_9_2_8/src/
eval `scramv1 runtime -sh`
scram b -j 8
cd /home/hep/ssb216/CMSSW_9_2_8/src/L1Trigger/L1JetEnergyCorrections/bin/
RunMatcherStage2L1Gen -N -1 --deltaR 0.25 -I ${INPUT} -O ${OUTPUT} --refDir l1GeneratorTree  --l1Dir l1UpgradeEmuTree

