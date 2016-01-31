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
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
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
    quantities = ['name', 'dataset_fraction', 'replica_fraction', 'block_fraction', 'block_completion']

    # Get site name and fractions for each site
    # yes, you prob shouldn't use shell=True, but CBA to figure out how to split the string for das_client
    grep_str = ' '.join(['site.%s' % q for q in quantities])
    out = check_output('das_client --query="site dataset=%s | grep %s"' % (dataset, grep_str), shell=True)

    site_dicts = []  # hold info about each site

    # Process the important lines, store in a dict for each site
    results = [x for x in out.split('\n') if 'Showing' not in x and x != '']
    for line in results:
        # Don't care if it's at a T1
        if line.startswith('T1'):
            continue
        sdict = {q : p for q, p in zip(quantities, line.split())}
        site_dicts.append(sdict)

    if verbose:
        # Print output for each site with fractions, colour coded
        print TColour.BLUE, dataset, TColour.ENDC
        print '\t %s' % ' - '.join(quantities)
        for sdict in site_dicts:
            fracs = [sdict[k] for k in quantities]
            status_col = TColour.RED
            if all([f == '100.00%' for f in fracs if not f.startswith('T')]):
                status_col = TColour.GREEN
            print '\t', status_col, ' - '.join(fracs), TColour.ENDC
    else:
        # Figure out if fully transferred anywhere, in which case print in green
        transferred = False
        for sdict in site_dicts:
            fracs = [sdict[k] for k in quantities]
            if all([f == '100.00%' for f in fracs if not f.startswith('T')]):
                transferred = True
                break

        status_col = TColour.GREEN if transferred else TColour.RED
        status_letter = 'v' if transferred else 'x'
        print status_col, status_letter, dataset, TColour.ENDC


def check_datasets(datasets, verbose):
    for dataset in datasets:
        check_dataset_presence(dataset, verbose)


if __name__ == "__main__":
    verbose = False
    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        verbose = True
    check_datasets(SAMPLES, verbose)
