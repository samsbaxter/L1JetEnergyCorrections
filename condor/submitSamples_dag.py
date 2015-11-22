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
import os
from cmsRunCondor import cmsRunCondor
import L1Trigger.L1JetEnergyCorrections.mc_samples as samples
from time import strftime, sleep
from subprocess import call


config = "../python/SimL1Emulator_Stage2.py"
outputDir = "/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_22Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_test"

datasets = ['QCDFlatSpring15BX25PU10to30HCALFix', 'QCDFlatSpring15BX25FlatNoPUHCALFix']

if __name__ == "__main__":
    # Run through datasets once to check all fine
    for dset in datasets:
        if not dset in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)
        if not samples.check_dataset(samples.samples[dset].inputDataset):
            raise RuntimeError("Dataset cannot be found in DAS: %s" % samples.samples[dset].inputDataset)

    status_names = []

    for dset in datasets:

        dset_opts = samples.samples[dset]
        print "*"*80
        print "Dataset key:", dset

        # Make the condor submit script for this dataset
        scriptName = '%s_%s_%s.condor' % (os.path.basename(config).replace(".py", ""), dset, strftime("%H%M%S"))
        print "Script Name:", scriptName
        job_dict = cmsRunCondor(['--config', config,
                                 '--outputDir', os.path.join(outputDir, dset),
                                 '--dataset', dset_opts.inputDataset,
                                 '--filesPerJob', str(dset_opts.unitsPerJob),
                                 '--totalFiles', str(dset_opts.totalUnits),
                                 '--outputScript', scriptName,
                                 '--dag'
                                 ])
