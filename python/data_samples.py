"""
Data samples to be used in CRAB3 configs

For each sample, we have a simple Dataset namedtuple. Fields are inputDataset,
unitsPerJob, and totalUnits. (see CRAB documentationf or meaning).
We then store all samples in a dict.

Usage:

from data_samples import samples

dataset = "Express_Run2015B_50ns"
config.General.requestName = dataset
config.Data.inputDataset = samples[dataset].inputDataset
config.Data.unitsPerJob = samples[dataset].unitsPerJob

totalUnits can take the values:
-1: run over all files in the dataset
0 - 1: run over this fraction of the dataset
>1: run over this many files

"""

from collections import namedtuple
import subprocess
import json


# some helper functions
def get_number_files(dataset):
    """Get total number of files in dataset"""
    cmds = ['das_client.py', '--query', 'summary dataset=%s' % dataset, '--format=json']
    output = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
    summary_dict = json.loads(output)
    return int(summary_dict['data'][0]['summary'][0]['nfiles'])


def check_dataset_exists(dataset):
    """Check dataset exists in DAS"""
    result = subprocess.call(['das_client.py', '--query', 'dataset dataset=%s' % dataset])
    return result == 0


# handy data structure to store some attributes for each dataset
Dataset = namedtuple("Dataset", "inputDataset unitsPerJob totalUnits")

# This dict holds ALL samples
samples = {

    "Express_Run2015B_50ns": Dataset(inputDataset='/ExpressPhysics/Run2015B-Express-v1/FEVT',
                                     unitsPerJob=15, totalUnits=-1),

    "Express_Run2015D_v4_25ns": Dataset(inputDataset='/ExpressPhysics/Run2015D-Express-v4/FEVT',
                                        unitsPerJob=10, totalUnits=-1),


}
