"""
Equivalent of the crab3 scripts, this creates jobs on the HTCondor system running
over various datasets.

User must select the correct config file, outputDir, and dataset(s).

The datasets must be the name of their keys in the samples dict (in mc_scamples or data_samples)
"""

import sys
import os
from cmsRunCondor import cmsRunCondor
import L1Trigger.L1JetEnergyCorrections.mc_samples as samples
from time import strftime, sleep


config = "../python/SimL1Emulator_Stage1_oldSetup.py"
outputDir = "/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDPhys14_AVE20BX25_default"
datasets = samples.samples_qcd_Phys14_AVE20BX25_AODSIM.keys()

if __name__ == "__main__":
    # Run through datasets once to check all fine
    for dset in datasets:
        if not dset in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)
        if not samples.check_dataset(samples.samples[dset].inputDataset):
            raise RuntimeError("Dataset cannot be found in DAS: %s" % samples.samples[dset].inputDataset)

    for dset in datasets:

        dset_opts = samples.samples[dset]
        print "*"*80
        print "Dataset key:", dset
 
        # to restrict total units run over
        if dset_opts.totalUnits > 1:
            totalUnits = dset_opts.totalUnits
        elif 0 < dset_opts.totalUnits <= 1:
            totalUnits = int(samples.get_number_files(dset_opts.inputDataset) * dset_opts.totalUnits)
        else:
            totalUnits = int(samples.get_number_files(dset_opts.inputDataset))  # make sure we reset
        print "Total units:", totalUnits

        scriptName = '%s_%s_%s.condor' % (os.path.basename(config).replace(".py", ""), dset, strftime("%H%M%S"))
        print "Script Name:", scriptName
        cmsRunCondor(['--config', config,
                      '--outputDir', outputDir+"/"+dset,
                      '--dataset', dset_opts.inputDataset,
                      '--filesPerJob', str(dset_opts.unitsPerJob),
                      '--totalFiles', str(totalUnits),
                      '--outputScript', scriptName,
                      "--verbose"])

        print "Sleeping for 60s to avoid hammering the queue..."
        sleep(60)
