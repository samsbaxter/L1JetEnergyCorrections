"""
Data samples to be used in CRAB3 configs

For each sample, we have a simple Dataset namedtuple. Fields are inputDataset
and unitsPerJob. We then store all samples in a dict.

Usage:

from samples import samples

dataset = "TTbarFall13PU20bx25"
config.General.requestName = dataset
config.Data.inputDataset = samples[dataset].inputDataset
config.Data.unitsPerJob = samples[dataset].unitsPerJob

totalUnits can take the values:
-1: run over all files in the dataset
0 - 1: run over this fraction of the dataset
>1: run over this many files

"""

from collections import namedtuple
import re
import das_client
import subprocess


# some helper functions
#
# THIS DOESN'T WORK. STALLS.
# COS SUBPROCESS/das_client IS A POS.
def get_number_files(dataset):
    # child = subprocess.Popen(['das_client.py','--query', 'summary dataset=%s' % dataset], stdout=subprocess.PIPE)
    # output = child.communicate()[0]
    # rc = child.returncode
    output = subprocess.check_output(['das_client.py','--query', 'summary dataset=%s' % dataset], stderr=subprocess.STDOUT)
    return int(re.search(r'nfiles +: (\d*)', output).group(1))


def check_dataset(dataset):
    return True


# handy data structure to store some attributes for each dataset
Dataset = namedtuple("Dataset", "inputDataset unitsPerJob totalUnits")

# This dict holds ALL samples
samples = {

    "Express_Run2015B_50ns": Dataset(inputDataset='/ExpressPhysics/Run2015B-Express-v1/FEVT',
                                     unitsPerJob=10, totalUnits=10),

}