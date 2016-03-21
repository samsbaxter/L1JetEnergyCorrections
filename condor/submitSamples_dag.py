#!/usr/bin/env python
"""
Equivalent of the crab3 scripts, this creates jobs on the HTCondor system running
over various datasets.

User must select the correct config file, outputDir, and dataset(s).

The datasets must be the name of their keys in the samples dict (in mc_samples or data_samples)

The results of each dataset in the datasets list will be stored in: <outputDir>/<dataset>/

outputDir should be on /hdfs !
"""
import sys
import importlib
import os
from cmsRunCondor import cmsRunCondor
import L1Trigger.L1JetEnergyCorrections.mc_samples as samples
from time import strftime


config = "../python/SimL1Emulator_Stage2_HF_MC.py"

sys.path.append(os.path.dirname(os.path.abspath(config)))  # nasty hack cos python packaging stoopid
cmssw_config = importlib.import_module(os.path.splitext(os.path.basename(config))[0],)
jst = cmssw_config.process.caloStage2Params.jetSeedThreshold.value()
print 'Running with JetSeedThreshold', jst

# CHANGE ME - to make a unique indentifier for each set of jobs
job_append = "Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst%s_RAWONLY_v2" % str(jst).replace('.', 'p')
outputDir = "/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/%s" % job_append

datestamp = strftime("%d_%b_%y")
logDir = "/storage/%s/L1JEC/%s/L1JetEnergyCorrections/%s/%s" % (os.environ['LOGNAME'], os.environ['CMSSW_VERSION'], datestamp, job_append)

datasets = ["QCDFlatFall15PU0to50NzshcalRaw", "QCDFlatFall15NoPU"]


if __name__ == "__main__":
    if not os.path.isdir(logDir):
        os.makedirs(logDir)

    # Run through datasets once to check all fine
    for dset in datasets:
        if dset not in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)
        # if not samples.check_dataset_exists(samples.samples[dset].inputDataset):
            # raise RuntimeError("Dataset cannot be found in DAS: %s" % samples.samples[dset].inputDataset)

    status_names = []

    for dset in datasets:

        dset_opts = samples.samples[dset]
        print "*" * 80
        print "Dataset key:", dset

        # Make the condor submit script for this dataset
        timestamp = strftime("%H%M%s")
        scriptName = '%s_%s_%s.condor' % (os.path.basename(config).replace(".py", ""), dset, timestamp)
        scriptName = os.path.join(logDir, scriptName)
        print "Script Name:", scriptName
        job_dict = cmsRunCondor(['--config', config,
                                 '--outputDir', os.path.join(outputDir, dset),
                                 '--dataset', dset_opts.inputDataset,
                                 '--filesPerJob', str(dset_opts.unitsPerJob),
                                 '--totalFiles', str(dset_opts.totalUnits),
                                 '--outputScript', scriptName,
                                 '--dag', os.path.join(logDir, 'cmsRunCondorDAG_%s.dag' % timestamp),
                                 '--log', os.path.join(logDir, dset)
                                 ])
