"""
Stage1-specific CRAB3 setup
"""


from crab3_cfg import config
from samples import samples, ptbins
from CRABAPI.RawCommand import crabCommand


# CHANGE ME - to make a unique indentifier for each set of jobs, e.g v2
job_append = "Stage1_newRCT"

# CHANGE ME - select dataset(s) to run over
datasets = []

for i, ptmin in enumerate(ptbins[:-1]):
    ptmax = ptbins[i+1]
    datasets.append("QCD_Pt-%dto%d_Phys14_AVE20BX25" % (ptmin, ptmax))
datasets.append("QCD_Pt-1800_Phys14_AVE20BX25")


if __name__ == "__main__":

    config.JobType.psetName = '../python/SimL1Emulator_Stage1_newRCT.py'

    # We want to put all the CRAB project directories from the tasks we submit
    # here into one common directory. That's why we need to set this parameter.
    config.General.workArea = 'l1ntuple_'+job_append

    for dset in datasets:
        if not dset in samples.keys():
            raise KeyError("Wrong dataset name")

        # requestName will be used for name of folder inside workArea,
        # and the name of the jobs on monitoring page
        config.General.requestName = dset+"_"+job_append
        config.Data.inputDataset = samples[dset].inputDataset
        config.Data.unitsPerJob = samples[dset].unitsPerJob

        crabCommand('submit', config=config)