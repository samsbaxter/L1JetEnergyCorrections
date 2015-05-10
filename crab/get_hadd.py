#!/usr/bin/env python

"""
This script goes through all the datasets in one set of crab jobs, and for each:
1) gets the job IDs for the firxt X% of jobs.
2) does crab getouput on thos job IDs
3) hadd these output files and put them in a sensible directory
4) remove old files

Writes out all the necessary commands to a file, crab_get_hadd.sh,
so you can check it over BEFORE running it.

Must be run in L1JetEnergyCorrections/crab directory.
"""


import subprocess
from glob import glob
import os
import stat
from CRABAPI.RawCommand import crabCommand


def get_hadd():
    """
    Loops through crab working area, and for each dataset outputs commands to
    get the files and hadd them, and putting them in sensible place.
    """

    # Working area - change me!
    crab_area = 'l1ntuple_GCT_QCDPhys14_newRCT_calibrated_hiPrec'

    # Write commands to file
    cmd_filename = 'crab_get_hadd.sh'
    with open(cmd_filename, "w") as cmd_file:

        # Loop over each dataset
        for f in os.listdir(crab_area):

            crab_dir = '{0}/{1}/'.format(crab_area, f)
            print 'Doing dir:', crab_dir
            if not os.path.isdir(crab_dir):
                continue

            # first get suitable output directory & file names
            # will put output dir in directory above this (assumes we're in L1JetEnergyCorrections/crab)
            # check to see if file already exists - in which case we skip this dataset
            out_dir = crab_dir.split("/")[0].replace("l1ntuple_GCT_", "")
            out_file = crab_dir.split("/")[1].replace("crab_", "L1Tree_")
            out_file += ".root"
            output_path = "../{0}/{1}".format(out_dir, out_file)
            if os.path.isfile(output_path):
                print "Skipping as output file already exists"
                continue

            # can either do datasets that are completely finished, or only
            # take a fraction of completed jobs
            res_status = crabCommand('status', crab_dir)
            completed = True
            n_jobs = len(res_status['jobs'])
            job_ids = []
            if completed:
                n_jobs_to_get = n_jobs
            else:
                n_jobs_to_get = int(round(n_jobs/5.0))

            # Get the requisite number of jobs, making sure they completed
            for i in range(1, n_jobs+1):
                if res_status['jobs'][str(i)]['State'] == 'finished':
                    job_ids.append(str(i))
                if len(job_ids) == n_jobs_to_get:
                    break
            if len(job_ids) != n_jobs_to_get:
                print "Not enough jobs finished! - skipping"
                print "Need %d jobs, only found %d " % (n_jobs_to_get, len(job_ids))
                continue

            # Get the output from the jobs
            print "Getting files %s from %s" % (job_ids, crab_dir)
            # wish I could use the CRAB API here but doesn't like --jobids option
            # res_get = crabCommand('getoutput', crab_dir, '--jobids %s' % (','.join(job_ids)))
            crab_get_cmd = 'crab getoutput --jobids {0} {1}'.format(','.join(job_ids), crab_dir)
            cmd_file.write(crab_get_cmd)
            cmd_file.write('\n')

            # hadd the files
            if not os.path.isdir("../"+out_dir):
                print "Making directory ../%s" % out_dir
                os.mkdir("../"+out_dir)

            hadd_cmd = "hadd -f {0} {1}".format(output_path, crab_dir+"/results/L1Tree*.root")
            cmd_file.write(hadd_cmd)
            cmd_file.write('\n')

            # Remove the crab output files
            rm_cmd = 'rm {0}/results/*.root'.format(crab_dir)
            cmd_file.write(rm_cmd)
            cmd_file.write('\n')

    # make file executable
    st = os.stat(cmd_filename)
    os.chmod(cmd_filename, st.st_mode | stat.S_IEXEC)
    print "Commands written to %s" % cmd_filename


if __name__ == '__main__':
    get_hadd()