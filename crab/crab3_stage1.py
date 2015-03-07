"""
Stage1-specific CRAB3 setup
"""


from crab3_cfg import config
from samples import samples


# CHANGE ME - to make a unique indentifier for each set of jobs, e.g v2
job_append = "_Stage1_newRCT"

# CHANGE ME - select dataset to run over, check it's ok
dataset = "TTbarFall13PU20bx25"


if not dataset in samples.keys():
    raise KeyError("Wrong dataset name")

config.JobType.psetName = '../python/SimL1Emulator_Stage1_newRCT.py'
config.General.requestName = "l1ntuple_" + dataset + job_append
config.Data.inputDataset = samples[dataset].inputDataset
config.Data.unitsPerJob = samples[dataset].unitsPerJob