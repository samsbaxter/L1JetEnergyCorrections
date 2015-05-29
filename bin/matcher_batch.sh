#!/bin/bash
# run with bsub -q 1nh "sh matcher_batch.sh <options>"
# MAKE SURE YOU UPDATE THE AREA, really should automate this
cd /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/work/r/raggleto/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/
RunMatcher $@
