#!/usr/bin/env python

"""
Submit checkCalib jobs on HTCondor.

- add in any pairs files you wish to run over (use absolute path)
- modify settings below (PU bins, append, etc)

Output files will be produced as follows: for pairs file, DATASET/pairs/pairs.root,
the output files will be put in DATASET/check/

Requires the htcondenser package: https://github.com/raggleton/htcondenser
"""

import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))  # to import binning.py
from binning import pairwise, eta_bins_central
from time import strftime
import htcondenser as ht
import condorCommon as cc


# List of pairs files to run over
PAIRS_FILES = [
'/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/pairs/pairs_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_testCalibratePU15to25_2048bins_maxCorr5.root'
]

# Maximum L1 pt to be included in plots (to avoid saturation effects)
MAX_L1_PT = 1022

# Select eta bins to run over
ETA_BINS = eta_bins_central

# Select PU bins to run over
PU_BINS = None  # None if you don't want to cut on PU
PU_BINS = [[0, 10], [15, 25], [30, 40]][1:2]

# String to append to output ROOT filename, depending on PU
# Note that the things in {} get formatted out later, see below
# Bit of dodgy magic
APPEND = "_PU{puMin}to{puMax}_maxPt{maxL1Pt}" if PU_BINS else "_maxPt{maxL1Pt}"

# Directory for logs (should be on /storage)
# Will be created automatically by htcondenser
datestamp = strftime("%d_%b_%y")
LOG_DIR = '/storage/%s/L1JEC/%s/L1JetEnergyCorrections/jobs/check/%s' % (os.environ['LOGNAME'], os.environ['CMSSW_VERSION'], datestamp)


def submit_all_checkCalib_dags(pairs_files, max_l1_pt, log_dir, append,
                               pu_bins, eta_bins, force_submit):
    """Create and submit DAG checkCalibration jobs for all pairs files.

    Parameters
    ----------
    pairs_files : list[str], optional
        List of pairs files to process. Must be full path.

    max_l1_pt : int, optional
        Maximum L1 pt to consider when making plots.

    log_dir : str, optional
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str, optional
        String to append to filenames to track various settings (e.g. PU bin).

    pu_bins : list[list[int, int]], optional
        List of PU bin edges.

    eta_bins : list[float], optional
        List of eta bin edges, including upper edge of last bin.

    force_submit : bool, optional
        If True, forces job submission even if proposed output files already exists.
        Otherwise, program quits before submission.
    """
    # Update the matcher script for the worker nodes
    setup_script = 'worker_setup.sh'
    cc.update_setup_script(setup_script, os.environ['CMSSW_VERSION'], os.environ['ROOTSYS'])

    # Update the hadd script for the worker node
    hadd_setup_script = 'cmssw_setup.sh'
    cc.update_hadd_setup_script(hadd_setup_script, os.environ['CMSSW_VERSION'])

    # Additional files to copy across - other modules. etc
    common_input_files = ['checkCalibration.py', 'binning.py', 'common_utils.py']
    common_input_files = [os.path.join(os.path.dirname(os.getcwd()), f) for f in common_input_files]

    # Submit a DAG for each pairs file
    for pfile in pairs_files:
        print 'Processing', pfile
        submit_checkCalib_dag(pairs_file=pfile, max_l1_pt=max_l1_pt,
                              log_dir=log_dir, append=append,
                              pu_bins=pu_bins, eta_bins=eta_bins,
                              common_input_files=common_input_files,
                              force_submit=force_submit)


def submit_checkCalib_dag(pairs_file, max_l1_pt, log_dir, append,
                          pu_bins, eta_bins, common_input_files,
                          force_submit=False):
    """Submit one checkCalibration DAG for one pairs file.

    This will run checkCalibration over exclusive and inclusive eta bins,
    and then finally hadd the results together.

    Parameters
    ----------
    pairs_files : str, optional
        Pairs file to process. Must be full path.

    max_l1_pt : int, optional
        Maximum L1 pt to consider when making plots.

    log_dir : str, optional
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str, optional
        String to append to filenames to track various settings (e.g. PU bin).

    pu_bins : list[list[int, int]], optional
        List of PU bin edges.

    eta_bins : list[float], optional
        List of eta bin edges, including upper edge of last bin.

    force_submit : bool, optional
        If True, forces job submission even if proposed output files
        already exists.
        Oherwise, program quits before submission.

    """
    cc.check_file_exists(pairs_file)

    # Setup output directory for check* files
    # e.g. if pairs file in DATASET/pairs/pairs.root
    # then output goes in DATASET/check/
    out_dir = os.path.dirname(os.path.dirname(pairs_file))
    out_dir = os.path.join(out_dir, 'check')
    cc.check_create_dir(out_dir, info=True)

    # Stem for output filename
    out_stem = os.path.splitext(os.path.basename(pairs_file))[0]
    out_stem = out_stem.replace("pairs_", "check_")

    # Input files for jobs
    input_files = common_input_files + [pairs_file]

    # Loop over PU bins
    # ---------------------------------------------------------------------
    pu_bins = pu_bins or [[-99, 999]]  # set ridiculous limits if no cut on PU
    for (pu_min, pu_max) in pu_bins:

        log_stem = 'checkCalib.$(cluster).$(process)'
        checkCalib_jobs = ht.JobSet(exe='python',
                                    copy_exe=False,
                                    filename='submit_checkCalib.condor',
                                    setup_script='worker_setup.sh',
                                    out_dir=log_dir, out_file=log_stem + '.out',
                                    err_dir=log_dir, err_file=log_stem + '.err',
                                    log_dir=log_dir, log_file=log_stem + '.log',
                                    cpus=1, memory='100MB', disk='100MB',
                                    transfer_hdfs_input=False,
                                    hdfs_store=out_dir,
                                    dag_mode=True)

        # For creating filenames later
        fmt_dict = dict(puMin=pu_min, puMax=pu_max, maxL1Pt=max_l1_pt)

        # Hold all output filenames
        check_output_files = []

        # Add exclusive eta bins to this JobSet
        for ind, (eta_min, eta_max) in enumerate(pairwise(eta_bins)):
            out_file = out_stem + "_%d" % ind + append.format(**fmt_dict) + '.root'
            out_file = os.path.join(out_dir, out_file)
            check_output_files.append(out_file)

            job_args = ['checkCalibration.py', pairs_file, out_file,
                        '--excl', '--maxPt', max_l1_pt,
                        '--PUmin', pu_min, '--PUmax', pu_max,
                        '--etaInd', ind]

            check_job = ht.Job(name='check_%d' % ind,
                               args=job_args,
                               input_files=input_files,
                               output_files=[out_file])

            checkCalib_jobs.add_job(check_job)

        # Add inclusive bins (central, forward, all)
        # remove the [0:1] to do all - currently central only 'cos HF broke
        for incl in ['central', 'forward', 'all'][0:1]:
            out_file = out_stem + "_%s" % incl + append.format(**fmt_dict) + '.root'
            out_file = os.path.join(out_dir, out_file)
            check_output_files.append(out_file)

            job_args = ['checkCalibration.py', pairs_file, out_file,
                        '--incl', '--maxPt', max_l1_pt,
                        '--PUmin', pu_min, '--PUmax', pu_max]
            if incl != 'all':
                job_args.append('--%s' % incl)

            check_job = ht.Job(name='check_%s' % incl,
                               args=job_args,
                               input_files=input_files,
                               output_files=[out_file])

            checkCalib_jobs.add_job(check_job)

        # Add hadd jobs
        # ---------------------------------------------------------------------
        log_stem = 'checkCalibHadd.$(cluster).$(process)'

        hadd_jobs = ht.JobSet(exe='hadd',
                              copy_exe=False,
                              filename='haddSmall.condor',
                              setup_script="cmssw_setup.sh",
                              out_dir=log_dir, out_file=log_stem + '.out',
                              err_dir=log_dir, err_file=log_stem + '.err',
                              log_dir=log_dir, log_file=log_stem + '.log',
                              cpus=1, memory='100MB', disk='20MB',
                              transfer_hdfs_input=False,
                              hdfs_store=out_dir,
                              dag_mode=True)

        # Construct final hadded file name
        final_file = os.path.join(out_dir, out_stem + append.format(**fmt_dict) + '.root')
        hadd_output = [final_file]
        hadd_args = hadd_output + check_output_files

        hadder = ht.Job(name='haddCheckCalib',
                        args=hadd_args,
                        input_files=check_output_files,
                        output_files=hadd_output)

        hadd_jobs.add_job(hadder)

        # Add all jobs to DAG, with necessary dependencies
        # ---------------------------------------------------------------------
        stem = 'checkCalib_%s_%s' % (strftime("%H%M%S"), cc.rand_str(3))
        checker_dag = ht.DAGMan(filename='%s.dag' % stem,
                                status_file='%s.status' % stem)
        for job in checkCalib_jobs:
            checker_dag.add_job(job)

        checker_dag.add_job(hadder, requires=[j for j in checkCalib_jobs])

        # Check if any of the output files already exists - maybe we mucked up?
        # ---------------------------------------------------------------------
        if not force_submit:
            for f in [final_file] + check_output_files:
                if os.path.isfile(f):
                    print 'ERROR: output file already exists - not submitting'
                    print 'FILE:', f
                    return 1

        # checker_dag.write()
        checker_dag.submit()


if __name__ == "__main__":
    force_submit = len(sys.argv) == 2 and sys.argv[1] == '-f'
    submit_all_checkCalib_dags(pairs_files=PAIRS_FILES, max_l1_pt=MAX_L1_PT,
                               log_dir=LOG_DIR, append=APPEND,
                               pu_bins=PU_BINS, eta_bins=ETA_BINS,
                               force_submit=force_submit)
