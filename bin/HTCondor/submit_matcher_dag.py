#!/usr/bin/env python

"""
Submit matcher jobs on HTCondor.

- add in any directories of NTuples (use absolute path)
- modify settings below (cuts, TDirectories, etc)

Output files will be produced as follows: for ntuples in XXX/DATASET, individual
pairs files will be in XXX/DATASET, whilst the hadded final file will be in
XXX/pairs

Requires the htcondenser package: https://github.com/raggleton/htcondenser

TODO: some fancier way of switching between MC & Data setups?
TODO: remove intermediate files? shouldn't be too hard, just tack extra jobs onto
DAG.
"""


import os
import sys
from time import strftime
from distutils.spawn import find_executable
from itertools import izip_longest
import math
import htcondenser as ht
import condorCommon as cc


# List of ntuple directories to run over
NTUPLE_DIRS = [
    '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/QCDFlatSpring15BX25PU10to30HCALFix',
]

# Choose executable to run - must be located using `which <EXE>`
EXE = 'RunMatcherStage2'  # For Stage 2 MC
# EXE = 'RunMatcherData'  # For Stage 2 DATA

# DeltaR(L1, RefJet) for matching
DELTA_R = 0.4

# Minimum pt cut on reference jets
PT_REF_MIN = 10

# TDirectory name for the L1 jets
L1_DIR = 'l1UpgradeSimTreeMP'
# L1_DIR = 'l1UpgradeEmuTree'

# TDirectory name for the reference jets
REF_DIR = 'l1ExtraTreeGenAk4'
# REF_DIR = 'l1JetRecoTree'

# String to append to output ROOT filename
# Note that the things in {} get formatted out later, see below
# Bit of dodgy magic
APPEND = 'MP_ak4_ref%dto5000_l10to5000_dr%s_testRRR' % (PT_REF_MIN, str(DELTA_R).replace('.', 'p'))

# Directory for logs (should be on /storage)
# Will be created automatically by htcondenser
datestamp = strftime("%d_%b_%y")
LOG_DIR = '/storage/%s/L1JEC/%s/L1JetEnergyCorrections/jobs/pairs/%s' % (os.environ['LOGNAME'], os.environ['CMSSW_VERSION'], datestamp)


def submit_all_matcher_dags(exe, ntuple_dirs, log_dir, append,
                            l1_dir, ref_dir, deltaR, ref_min_pt,
                            force_submit):
    """Create and submit DAG checkCalibration jobs for all pairs files.

    Parameters
    ----------
    exe : str
        Name of executable.

    ntuple_dirs : list[str]
        List of directories with L1Ntuples to run over.

    log_dir : str, optional
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str, optional
        String to append to filenames to track various settings (e.g. deltaR cut).

    l1_dir : str
        Name of TDirectory in Ntuple that holds L1 jets.

    ref_dir : str
        Name of TDirectory in Ntuple that holds reference jets.

    deltaR : float
        Maximum deltaR(L1, Ref) for a match.

    ref_min_pt : float
        Minimum pT cut on reference jets to be considered for matching.

    force_submit : bool, optional
        If True, forces job submission even if proposed output files
        already exists.
        Oherwise, program quits before submission.
    """
    # Update the matcher script for the worker nodes
    setup_script = 'worker_setup.sh'
    cc.update_setup_script(setup_script, os.environ['CMSSW_VERSION'], os.environ['ROOTSYS'])

    # Update the hadd script for the worker node
    hadd_setup_script = 'cmssw_setup.sh'
    cc.update_hadd_setup_script(hadd_setup_script, os.environ['CMSSW_VERSION'])

    # Submit a DAG for each pairs file
    for ndir in ntuple_dirs:
        print '>>> Processing', ndir
        submit_matcher_dag(exe=exe, ntuple_dir=ndir, log_dir=log_dir,
                           l1_dir=l1_dir, ref_dir=ref_dir,
                           deltaR=deltaR, ref_min_pt=ref_min_pt,
                           append=append, force_submit=force_submit)


def submit_matcher_dag(exe, ntuple_dir, log_dir, l1_dir, ref_dir, deltaR, ref_min_pt,
                       append, force_submit):
    """Submit one matcher DAG for one directory of ntuples.

    This will run `exe` over all Ntuple files and then hadd the results together.

    Parameters
    ----------
    exe : str
        Name of executable.

    ntuple_dir : str
        Name of directory with L1Ntuples to run over.

    log_dir : str
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str
        String to append to filenames to track various settings (e.g. deltaR cut).

    l1_dir : str
        Name of TDirectory in Ntuple that holds L1 jets.

    ref_dir : str
        Name of TDirectory in Ntuple that holds reference jets.

    deltaR : float
        Maximum deltaR(L1, Ref) for a match.

    ref_min_pt : float
        Minimum pT cut on reference jets to be considered for matching.

    force_submit : bool
        If True, forces job submission even if proposed output files
        already exists.
        Oherwise, program quits before submission.
    """
    # JobSet for each matching job
    log_stem = 'matcher.$(cluster).$(process)'

    matcher_jobs = ht.JobSet(exe=find_executable(exe),
                             copy_exe=True,
                             filename='submit_matcher.condor',
                             setup_script=None,
                             out_dir=log_dir, out_file=log_stem + '.out',
                             err_dir=log_dir, err_file=log_stem + '.err',
                             log_dir=log_dir, log_file=log_stem + '.log',
                             cpus=1, memory='100MB', disk='100MB',
                             transfer_hdfs_input=False,
                             share_exe_setup=True,
                             hdfs_store=ntuple_dir,
                             dag_mode=True)

    # DAG for jobs
    stem = 'matcher_%s_%s' % (strftime("%H%M%S"), cc.rand_str(3))
    matcher_dag = ht.DAGMan(filename='%s.dag' % stem,
                            status_file='%s.status' % stem)

    # For creating filenames later
    fmt_dict = dict()

    # Hold all output filenames
    match_output_files = []

    # Additional files to copy across - JEC, etc
    common_input_files = []

    # Add matcher job for each ntuple file
    for ind, ntuple in enumerate(os.listdir(ntuple_dir)):
        # if ind > 10:
            # break
        # Skip non-ntuple files
        if not ntuple.endswith('.root') or ntuple.startswith('pairs'):
            continue

        ntuple_abspath = os.path.join(ntuple_dir, ntuple)

        # Construct output name
        ntuple_name = os.path.splitext(ntuple)[0]
        pairs_file = '%s_%s.root' % (ntuple_name.replace('L1Tree_', 'pairs_'),
                                     append.format(**fmt_dict))
        out_file = os.path.join(ntuple_dir, pairs_file)
        match_output_files.append(out_file)

        # Add matching job
        job_args = ['-I', ntuple_abspath, '-O', out_file,
                    '--refDir', ref_dir, '--l1Dir', l1_dir,
                    '--draw 0', '--deltaR', deltaR, '--refMinPt', ref_min_pt]

        input_files = common_input_files + [ntuple_abspath]

        match_job = ht.Job(name='match_%d' % ind,
                           args=job_args,
                           input_files=input_files,
                           output_files=[out_file])

        matcher_jobs.add_job(match_job)
        matcher_dag.add_job(match_job)

    # Construct final filename
    # ---------------------------------------------------------------------
    final_file = 'pairs_%s_%s.root' % (os.path.basename(ntuple_dir.rstrip('/')),
                                       append.format(**fmt_dict))
    final_dir = os.path.join(os.path.dirname(ntuple_dir.rstrip('/')), 'pairs')
    cc.check_create_dir(final_dir, info=True)
    final_file = os.path.join(final_dir, final_file)

    # Check if any of the output files already exists - maybe we mucked up?
    # ---------------------------------------------------------------------
    if not force_submit:
        for f in [final_file] + match_output_files:
            if os.path.isfile(final_file):
                print 'ERROR: output file already exists - not submitting'
                print 'FILE:', f
                return 1

    add_hadd_jobs(matcher_dag, matcher_jobs.jobs.values(), final_file, log_dir)

    # Submit
    # ---------------------------------------------------------------------
    # matcher_dag.write()
    matcher_dag.submit()
    print 'DAGstatus.py %s.status' % stem
    return 0


def add_hadd_jobs(dagman, jobs, final_file, log_dir):
    """Add necessary hadd jobs to DAG. All jobs will be hadded together to make
    `final_file`.

    DAGs can only accept a maximum number of arguments, so we have to split
    up hadd-ing into groups. Therefore we need an intermediate layer of hadd
    jobs, and then finally hadd those intermediate output files

    Parameters
    ----------
    dagman : DAGMan
        DAGMan object to add jobs to.

    jobs : list[Job]
        Collection of Jobs to be hadd-ed together.

    final_file : str
        Final hadd-ed filename.
    """
    group_size = 200  # max files per hadding job
    # adjust to avoid hadding 1 file by itself
    if len(jobs) % group_size == 0:
        group_size = 199
    # calculate number of intermediate hadd jobs required
    n_inter_jobs = int(math.ceil(len(jobs) * 1. / group_size))

    log_stem = 'matcherHadd.$(cluster).$(process)'

    hadd_jobs = ht.JobSet(exe='hadd',
                          copy_exe=False,
                          filename='haddBig.condor',
                          setup_script=None,
                          out_dir=log_dir, out_file=log_stem + '.out',
                          err_dir=log_dir, err_file=log_stem + '.err',
                          log_dir=log_dir, log_file=log_stem + '.log',
                          cpus=1, memory='100MB', disk='1GB',
                          transfer_hdfs_input=False,
                          share_exe_setup=True,
                          hdfs_store=os.path.dirname(final_file),
                          dag_mode=True)

    if n_inter_jobs == 1:
        hadd_input = [j.output_files[0] for j in jobs]
        hadd_args = [final_file] + hadd_input
        hadd_job = ht.Job(name='finalHadd',
                          args=hadd_args,
                          input_files=hadd_input,
                          output_files=[final_file])
        hadd_jobs.add_job(hadd_job)
        dagman.add_job(hadd_job, requires=jobs)
    else:
        # Go through groups of Jobs, make intermediate hadd files in same dir
        # as final file
        intermediate_jobs = []
        for i, job_group in enumerate(grouper(jobs, group_size)):
            # Note, job_group is guaranteed to be length group_size, and is
            # padded with None if there arent' that many entries. So need to
            # check j is a ht.Job
            hadd_input = [j.output_files[0] for j in job_group if j]
            inter_file = 'hadd_inter_%d_%s.root' % (i, cc.rand_str(5))
            inter_file = os.path.join(os.path.dirname(final_file), inter_file)
            hadd_args = [inter_file] + hadd_input
            hadd_job = ht.Job(name='interHadd%d' % i,
                              args=hadd_args,
                              input_files=hadd_input,
                              output_files=[inter_file])
            hadd_jobs.add_job(hadd_job)
            dagman.add_job(hadd_job, requires=jobs)
            intermediate_jobs.append(hadd_job)

        # Add final hadd job for intermediate files
        hadd_input = [j.output_files[0] for j in intermediate_jobs]
        hadd_args = [final_file] + hadd_input
        hadd_job = ht.Job(name='finalHadd',
                          args=hadd_args,
                          input_files=hadd_input,
                          output_files=[final_file])
        hadd_jobs.add_job(hadd_job)
        dagman.add_job(hadd_job, requires=intermediate_jobs)


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Taken from https://docs.python.org/2/library/itertools.html#recipes
    e.g.
    >>> grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


if __name__ == "__main__":
    force_submit = len(sys.argv) == 2 and sys.argv[1] == '-f'
    sys.exit(submit_all_matcher_dags(exe=EXE, ntuple_dirs=NTUPLE_DIRS, log_dir=LOG_DIR,
                                     l1_dir=L1_DIR, ref_dir=REF_DIR,
                                     deltaR=DELTA_R, ref_min_pt=PT_REF_MIN,
                                     append=APPEND, force_submit=True))
