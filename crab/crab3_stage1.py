"""
Stage1-specific CRAB3 setup

Run with 'python crab3_stage1.py'
"""


from L1Trigger.L1JetEnergyCorrections.crab3_cfg import config
import L1Trigger.L1JetEnergyCorrections.samples as samples
from CRABAPI.RawCommand import crabCommand
import httplib


# CHANGE ME - to make a unique indentifier for each set of jobs, e.g v2
job_append = "Stage1_QCDSpring15_newRCTv2"

# CHANGE ME - select dataset(s) to run over
datasets = samples.samples_qcd_Spring15_AVE20BX25.keys()

if __name__ == "__main__":


    # We want to put all the CRAB project directories from the tasks we submit
    # here into one common directory. That's why we need to set this parameter.
    config.General.workArea = 'l1ntuple_'+job_append

    config.JobType.psetName = '../python/SimL1Emulator_Stage1_newRCT.py'

    # Run through datasets once to check all fine
    for dset in datasets:
        if not dset in samples.samples.keys():
            raise KeyError("Wrong dataset name:", dset)

    for dset in datasets:
        print dset
        # requestName will be used for name of folder inside workArea,
        # and the name of the jobs on monitoring page
        config.General.requestName = dset+"_"+job_append
        config.Data.inputDataset = samples.samples[dset].inputDataset
        config.Data.unitsPerJob = samples.samples[dset].unitsPerJob

        # to restrict total units run over
        # comment it out to run over all
        # if samples.samples[dset].totalUnits > 0:
        #     config.Data.totalUnits = samples.samples[dset].totalUnits
        #     print samples.samples[dset].totalUnits
        # else:
        #     config.Data.totalUnits = 100000000  # make sure we reset

        try:
            crabCommand('submit', config=config)
        except httplib.HTTPException as e:
            print "Cannot submit dataset %s - are you sure it is right?" % d
            raise