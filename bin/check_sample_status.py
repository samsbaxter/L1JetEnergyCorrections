#!/usr/bin/env python
"""
Script to check whether samples are at a T2 (fully).
Run by doing:

./check_sample_status.py

For each dataset in SAMPLES, will print out the sample in red with a 'x'
if not fully at any T2.
If it is fully present at atleast 1 T2, then it will print in green with a 'v'.

For more detailed info about fractions for each T2 site, use the verbose switch,
./check_sample_status.py -v

It ain't pretty, but it works.

TODO: use JSON output instead for fewer calls to das_client? (Currently 5/sample)
"""


import sys
from subprocess import check_output


SAMPLES = [
    # exclusive
    "/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12_ext1-v1/GEN-SIM-RAW",
    "/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12_ext1-v1/GEN-SIM-RAW",
    "/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12_ext1-v1/GEN-SIM-RAW",
    "/QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    # inclusive
    "/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/RunIIFall15DR76-25nsFlat10to25TSG_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/RunIIFall15DR76-25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW",
    "/QCD_Pt-15to7000_TuneCUETP8M1_Flat_13TeV_pythia8/RunIIFall15DR76-25nsNoPURaw_magnetOn_76X_mcRun2_asymptotic_v12-v1/GEN-SIM-RAW"
]


class TColour:
    """For terminal coloured output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_dataset_presence(dataset, verbose=False):
    """Check to see if dataset is present at a T2

    Parameters
    ----------

    dataset : str
        Name of dataset
    verbose : bool, optional
        True for more printout
    """
    # a horrible way to store info about all sites
    quantities = {'dataset_fraction': None, 'replica_fraction': None, 'block_fraction': None, 'block_completion': None}

    # yes, you prob shouldn't use shell=True, but cba to figure out how to split the string for das_client
    out = check_output('das_client.py --query="site dataset=%s"' % dataset, shell=True)
    sites = [x for x in out.split('\n') if 'Showing' not in x and x != '']

    for quantity in quantities:
        out = check_output('das_client --query="site dataset=%s | grep site.%s"' % (dataset, quantity), shell=True)
        result = [x for x in out.split('\n') if 'Showing' not in x and x != '']
        quantities[quantity] = result

    if verbose:
        # Print output for each site with fractions, colour coded
        print TColour.OKBLUE, dataset, TColour.ENDC
        print '\t SITE - %s' % ' - '.join(quantities.keys())
        for i, site in enumerate(sites):
            if site.startswith('T1'):
                continue

            line = [site]
            fractions = [quantities[k][i] for k in quantities]
            line.extend(fractions)
            status_col = TColour.FAIL
            if all([x == '100.00%' for x in fractions]):
                status_col = TColour.OKGREEN
            print '\t', status_col, ' - '.join(line), TColour.ENDC
    else:
        # Figure out if fully transferred anywhere, in which case print in green
        transferred = False
        for i, site in enumerate(sites):
            if site.startswith('T1'):
                continue
            fractions = [quantities[k][i] for k in quantities]
            status_col = TColour.FAIL
            if all([x == '100.00%' for x in fractions]):
                transferred = True
                break

        status_col = TColour.OKGREEN if transferred else TColour.FAIL
        status_let = 'v' if transferred else 'x'
        print status_col, status_let, dataset, TColour.ENDC


def check_datasets(datasets, verbose):
    for dataset in datasets:
        check_dataset_presence(dataset, verbose)


if __name__ == "__main__":
    verbose = False
    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        verbose = True
    check_datasets(SAMPLES, verbose)
