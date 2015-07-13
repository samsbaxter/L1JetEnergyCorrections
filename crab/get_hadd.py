#!/usr/bin/env python

"""
This script goes through all the datasets in one set of crab jobs, and for
each makes a shell script that:

1) gets the job IDs for successfully finished jobs IDs
2) does crab getouput on those job IDs
3) hadd these output files and put them in a sensible directory
4) remove old files

Writes out all the necessary commands to a file, crab_get_hadd_<timestamp>.sh,
so you can check it over BEFORE running it.

Also writes a simple shell script (crab_get_hadd_all.sh) to run all
the crab_get_hadd_*.sh in one go.

Must be run in L1JetEnergyCorrections/crab directory.

For various options (such as only get a fraction of jobs), use --help/-h
"""


import argparse
import subprocess
from glob import glob
import os
import stat
from CRABAPI.RawCommand import crabCommand
import sys
from time import strftime


env_shebang = '#!/bin/bash'

def get_hadd(in_args=sys.argv[1:]):
    """
    Loops through crab working area, and for each dataset outputs commands to
    get the files and hadd them, and putting them in sensible place.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("crab_dir", help='Working area')
    parser.add_argument("--completed", action='store_true',
        help="Only make command file if all jobs have finished successfully")
    parser.add_argument("--fraction", type=float, default=0.9,
        help="Specify fraction of jobs that must have finished successfully. " \
             "--completed overrides this option. Note that if a larger " \
             "fraction of jobs have finished successfully, " \
             "they will also be retrieved (to avoid this, use --strict).")
    parser.add_argument("--strict", action='store_true',
        help="If using --fraction, this ensures that exactly that fraction " \
             "of jobs are retrieved.")
    args = parser.parse_args(args=in_args)

    crab_area = args.crab_dir.rstrip('/')  # important!

    cmd_filenames = []  # to store shell script filenames for later

    # Loop over each dataset
    for f in os.listdir(crab_area):

        crab_dir = '{0}/{1}/'.format(crab_area, f)
        print ' ++++ Doing dir:', crab_dir
        if not os.path.isdir(crab_dir):
            continue
        cmd_filename = 'crab_get_hadd_%s.sh' % (strftime("%H%M%S"))

        # first get suitable output directory & file names
        # will put output dir in directory above this (assumes we're in L1JetEnergyCorrections/crab)
        # check to see if file already exists - in which case we skip this dataset
        # if "GCT" in crab_dir:
        #     out_dir = crab_dir.split("/")[0].replace("l1ntuple_GCT_", "")
        # elif "Stage1" in crab_dir:
        #     out_dir = crab_dir.split("/")[0].replace("l1ntuple_Stage1_", "")
        out_dir = crab_dir.split("/")[0].replace("l1ntuple_", "")
        out_file = crab_dir.split("/")[1].replace("crab_", "L1Tree_")
        out_file += ".root"
        output_path = "../{0}/{1}".format(out_dir, out_file)
        if os.path.isfile(output_path):
            print "Skipping as output file already exists"
            continue

        # if output directory doens't exists, add a command to make it
        if not os.path.isdir('../'+out_dir):
            print 'Making dir ../'+out_dir
            os.mkdir('../'+out_dir)

        # can either do datasets that are completely finished, or only
        # take a fraction of completed jobs
        # strict = do *exactly* the fraction of jobs, and no more
        completed = args.completed
        fraction = args.fraction
        strict = args.strict
        res_status = crabCommand('status', crab_dir)
        n_jobs = len(res_status['jobs'])
        job_ids = []
        if completed:
            n_jobs_to_get = n_jobs
        else:
            n_jobs_to_get = int(round(fraction*n_jobs))

        # Get the requisite number of jobs (or more), making sure they completed
        for i in range(1, n_jobs+1):
            if res_status['jobs'][str(i)]['State'] == 'finished':
                job_ids.append(str(i))
            if strict and (len(job_ids) == n_jobs_to_get):
                break

        if len(job_ids) < n_jobs_to_get:
            print " ---- Not enough jobs finished! - skipping"
            print "Need %d jobs, only found %d " % (n_jobs_to_get, len(job_ids))
            continue

        # Write commands to file
        with open(cmd_filename, "w") as cmd_file:

            # START WRITING COMMANDS TO FILE:
            cmd_file.write("%s\n" % env_shebang)

            # Get the output from the jobs
            # check that there are actually that many files - if not, repeat several times
            # if still haven't got all the files, then quit with an error
            print "Will get %d files %s from %s" % (len(job_ids), job_ids, crab_dir)
            # wish I could use the CRAB API here but doesn't like --jobids option
            # res_get = crabCommand('getoutput', crab_dir, '--jobids %s' % (','.join(job_ids)))
            crab_get_cmd = '\tcrab getoutput --jobids {0} {1}\n'.format(','.join(job_ids), crab_dir)
            cmd_file.write(crab_get_cmd)
            cmd_file.write("reps=10\n")
            cmd_file.write("while [ $(ls %s/results/*.root | wc -l) -lt %d ] && [ $reps -gt 0 ]\n" % (crab_dir , len(job_ids)))
            cmd_file.write("do\n")
            cmd_file.write(crab_get_cmd)
            # cmd_file.write('\n')
            cmd_file.write('\treps=$(($reps-1))\n')
            cmd_file.write("done\n")

            cmd_file.write("if [ $(ls %s/results/*.root | wc -l) -lt %d ]\n" % (crab_dir , len(job_ids)))
            cmd_file.write("then\n")
            cmd_file.write('\techo "Could not get all files. Please check! Exiting."\n')
            cmd_file.write('\texit 1\n')
            cmd_file.write("fi\n")

            # hadd the files
            if not os.path.isdir("../"+out_dir):
                print "Making directory ../%s" % out_dir
                os.mkdir("../"+out_dir)

            hadd_cmd = "hadd -f {0} {1}".format(output_path, crab_dir+"/results/L1Tree*.root")
            cmd_file.write(hadd_cmd)
            cmd_file.write('\n')

            print "Will make output file %s" % output_path

            # Remove the crab output files
            rm_cmd = 'rm {0}/results/*.root'.format(crab_dir)
            cmd_file.write(rm_cmd)
            cmd_file.write('\n')

            # If we can get the files, add to get_hadd_all script
            cmd_filenames.append(cmd_filename)

        # make file executable
        st = os.stat(cmd_filename)
        os.chmod(cmd_filename, st.st_mode | stat.S_IEXEC)
        print "Commands written to %s" % cmd_filename

    # Now write a simple script to run all the produced scripts
    all_filename = 'crab_get_hadd_all.sh'
    with open(all_filename, 'w') as f_all:
        f_all.write("%s\n" % env_shebang)
        for cmd in cmd_filenames:
            f_all.write("./%s\n" % cmd)

    st = os.stat(all_filename)
    os.chmod(all_filename, st.st_mode | stat.S_IEXEC)
    print "All-in-one script written to %s" % all_filename

if __name__ == '__main__':
    get_hadd()
