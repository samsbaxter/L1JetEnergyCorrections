#!/bin/bash
# run with qsub -q hep.q -l h_rt=1:0:0 -m bea -M samuel.baxter@desy.de -t 0-15:1 "calibration_batch.sh"

((--SGE_TASK_ID))

INPUT=/vols/cms/ssb216/matchedFiles/pairs.root

mkdir -p /vols/cms/ssb216/calibFiles/fittedFiles

OUTPUT=/vols/cms/ssb216/calibFiles/fittedFiles/calib_${SGE_TASK_ID}.root

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc530
cd /home/hep/ssb216/CMSSW_9_2_8/src/
eval `scramv1 runtime -sh`
scram b -j 8
cd /home/hep/ssb216/CMSSW_9_2_8/src/L1Trigger/L1JetEnergyCorrections/bin/
python runCalibration.py ${INPUT} ${OUTPUT} --PUmin 50 --PUmax 60 --stage2 --etaInd ${SGE_TASK_ID}
