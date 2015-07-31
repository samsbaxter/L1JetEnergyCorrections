"""
Stage1-specific CRAB3 setup

Run with 'python crab3_stage1.py'
"""


from L1Trigger.L1JetEnergyCorrections.crab3_cfg import config
import L1Trigger.L1JetEnergyCorrections.samples as samples
from CRABAPI.RawCommand import crabCommand
import httplib


# CHANGE ME - to make a unique indentifier for each set of jobs, e.g v2
job_append = "Stage1_QCDSpring15_AVE20BX25_newRCTv2_calibrated_31_Jul_15"

# CHANGE ME - select dataset(s) to run over
datasets = samples.samples_qcd_Spring15_AVE20BX25

if __name__ == "__main__":


    # We want to put all the CRAB project directories from the tasks we submit
    # here into one common directory. That's why we need to set this parameter.
    config.General.workArea = 'l1ntuple_'+job_append

    config.JobType.psetName = '../python/SimL1Emulator_Stage1_newRCT.py'

    # Run through datasets once to check all fine
    for dset in datasets:
        if not dset in samples.samples.keys():
            raise KeyError("Wrong dataset key name:", dset)
        if not samples.check_dataset(samples.samples[dset].inputDataset):
            raise RuntimeError("Dataset cannot be found in DAS: %s" % samples.samples[dset].inputDataset)

    for dset in datasets:
        dset_opts = samples.samples[dset]
        print dset
        # requestName will be used for name of folder inside workArea,
        # and the name of the jobs on monitoring page
        config.General.requestName = dset+"_"+job_append
        config.Data.inputDataset = dset_opts.inputDataset
        config.Data.unitsPerJob = dset_opts.unitsPerJob

        # to restrict total units run over
        # comment it out to run over all
        if dset_opts.totalUnits > 1:
            config.Data.totalUnits = dset_opts.totalUnits
        elif 0 < dset_opts.totalUnits < 1:
            config.Data.totalUnits = int(samples.get_number_files(dset_opts.inputDataset) * dset_opts.totalUnits)
        else:
            config.Data.totalUnits = 1000000000  # make sure we reset

        print config.Data.totalUnits, "total units"

        try:
            crabCommand('submit', config=config)
        except httplib.HTTPException as e:
            print "Cannot submit dataset %s - are you sure it is right?" % d
            raise