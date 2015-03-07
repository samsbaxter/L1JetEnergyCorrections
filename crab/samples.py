"""
Setup samples here to be used in CRAB3 configs

For each sample, we have a simple Dataset namedtuple. Fields are inputDataset
and unitsPerJob. We then store all samples in a dict.

Usage:

from samples import samples

dataset = "TTbarFall13PU20bx25"
config.General.requestName = dataset
config.Data.inputDataset = samples[dataset].inputDataset
config.Data.unitsPerJob = samples[dataset].unitsPerJob

"""

from collections import namedtuple

Dataset = namedtuple("Dataset", "inputDataset unitsPerJob")

samples = {

    "TTbarFall13PU20bx25": Dataset(inputDataset='/TT_Tune4C_13TeV-pythia8-tauola/Fall13dr-tsg_PU20bx25_POSTLS162_V2-v1/GEN-SIM-RAW',
                                    unitsPerJob=100),

    "QCDFlatSpring14": Dataset(inputDataset='/QCD_Pt-15to3000_Tune4C_Flat_13TeV_pythia8/Spring14dr-Flat20to50_POSTLS170_V5-v1/GEN-SIM-RAW',
                                unitsPerJob=50)

}