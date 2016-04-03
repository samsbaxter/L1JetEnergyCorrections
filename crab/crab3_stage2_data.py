"""
Stage2-specific CRAB3 setup for running with Data

Run with 'python crab3_stage2.py'
"""


from L1Trigger.L1JetEnergyCorrections.crab3_cfg import config
import L1Trigger.L1JetEnergyCorrections.data_samples as samples
from CRABAPI.RawCommand import crabCommand
import httplib
import importlib
import os
import sys


# CMSSW CONFIG TO RUN
PY_CONFIG = '../python/SimL1Emulator_Stage2_HF_Data.py'

# Auto-retrieve jet seed threshold in config
# sys.path.append(os.path.dirname(os.path.abspath(PY_CONFIG)))  # nasty hack cos python packaging stoopid
# cmssw_config = importlib.import_module(os.path.splitext(os.path.basename(PY_CONFIG))[0],)
# jst = cmssw_config.process.caloStage2Params.jetSeedThreshold.value()
# print 'Running with JetSeedThreshold', jst

# CHANGE ME - to make a unique indentifier for each set of jobs, e.g v2
job_append = "Stg2_Run2015D_run259721_zeroBias_3Apr_jetmetUpdateForJoe_L1JEC"
# job_append = "Stg2_Run2015D_run259721_zeroBias_intv14p0Layer1_noL1JEC_jst%s" % str(jst).replace('.', 'p')

# CHANGE ME - select dataset(s) keys to run over - see data_samples.py
datasets = ["ZeroBiasReReco_Run2015D_0_noReco", "ZeroBiasReReco_Run2015D_1_noReco", "ZeroBiasReReco_Run2015D_2_noReco", "ZeroBiasReReco_Run2015D_3_noReco", "ZeroBiasReReco_Run2015D_4_noReco"]

if __name__ == "__main__":

    # We want to put all the CRAB project directories from the tasks we submit
    # here into one common directory. That's why we need to set this parameter.
    config.General.workArea = 'l1ntuple_' + job_append

    config.JobType.psetName = PY_CONFIG

    # Run through datasets once to check all fine
    for dset in datasets:
        if dset not in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)
        if not samples.check_dataset_exists(samples.samples[dset].inputDataset):
            raise RuntimeError("Dataset cannot be found in DAS: %s" % samples.samples[dset].inputDataset)

    for dset in datasets:
        dset_opts = samples.samples[dset]
        print dset

        # requestName will be used for name of folder inside workArea,
        # and the name of the jobs on monitoring page
        config.General.requestName = dset + "_" + job_append
        config.Data.inputDataset = dset_opts.inputDataset
        config.Data.useParent = dset_opts.useParent
        config.Data.unitsPerJob = dset_opts.unitsPerJob
        config.Data.runRange = '259721'
        config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt'
        config.Data.splitting = 'LumiBased'
        config.JobType.inputFiles = ['../python/Fall15_25nsV2_DATA.db']

        # # to restrict total units run over
        # # comment it out to run over all
        # if dset_opts.totalUnits > 1:
        #     config.Data.totalUnits = dset_opts.totalUnits
        # elif 0 < dset_opts.totalUnits < 1:
        #     config.Data.totalUnits = int(samples.get_number_files(dset_opts.inputDataset) * dset_opts.totalUnits)
        # else:
        #     config.Data.totalUnits = 10000000000  # make sure we reset

        # print config.Data.totalUnits, "total units"

        try:
            crabCommand('submit', config=config)
        except httplib.HTTPException as e:
            print "Cannot submit dataset %s - are you sure it is right?" % dset
            raise
