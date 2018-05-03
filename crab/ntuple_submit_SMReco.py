from L1Trigger.L1JetEnergyCorrections.crab3_lumibased_cfg import config
import L1Trigger.L1JetEnergyCorrections.mc_samples as samples
from CRABAPI.RawCommand import crabCommand
import httplib
import importlib
import os
import sys


# Name of the CMSSW configuration file
PY_CONFIG =  '../python/ntuple_maker_L1PF_Nov_2017.py'
job_append = 'JetHTReReco_B_HF_L1JEC_03052018_ICL'
datasets = ["JetHT_Run2016B-07Aug17-v1_AOD_RecoRAW"]
# config.JobType.inputFiles = ['Summer15_25nsV6_DATA.db']
if __name__ == "__main__":
    config.General.workArea = 'l1ntuple_' + job_append

    config.JobType.psetName = PY_CONFIG

    for dset in datasets:
        if dset not in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)

    for dset in datasets:
        print dset

        dset_opts = samples.samples[dset]

        config.General.requestName = dset + "_" + job_append
        config.Data.inputDataset = dset_opts.inputDataset
        config.Data.useParent = dset_opts.useParent
        config.Data.unitsPerJob = dset_opts.unitsPerJob
        config.Data.totalUnits = dset_opts.totalUnits



        try:
            crabCommand('submit', config=config)
        except httplib.HTTPException as e:
            print "Cannot submit dataset %s - are you sure it is right?" % dset
            raise


