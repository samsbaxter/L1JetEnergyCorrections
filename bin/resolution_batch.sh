#!/bin/bash
# run with bsub -q 8nh "sh resolution_batch.sh <options>"
cd /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/bin
python makeResolutionPlots.py $@
