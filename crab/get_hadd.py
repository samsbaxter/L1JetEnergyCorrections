#!/usr/bin/env python

"""
This script goes through all the datasets in one set of crab jobs, and for each:
1) gets the job IDs for the firxt X% of jobs.
2) does crab getouput on thos job IDs
3) hadd these output files and put them in a sensible directory
4) remove old files

Writes out all the necessary commands to a file, crab_get_hadd.sh,
so you can check it over BEFORE running it
"""


import subprocess
from glob import glob
import os
from CRABAPI.RawCommand import crabCommand


# Working area - change me!
crab_area = 'l1ntuple_GCT_QCDPhys14_newRCT_calibrated_4'

with open('crab_get_hadd.sh', "w") as cmd_file:

    # Loop over each dataset
    for f in os.listdir(crab_area):
        crab_dir = 'l1ntuple_GCT_QCDPhys14_newRCT_calibrated_4/%s/' % f
        print crab_dir
        if not os.path.isdir(crab_dir):
            continue
        res_status = crabCommand('status', crab_dir)
        # print res_status

        # Get 1/5th of jobs, and make sure they completed successfully
        n_jobs = len(res_status['jobs'])
        n_jobs_to_get = int(round(n_jobs/5.0))
        job_ids = []

        for i in range(1, n_jobs):
            if res_status['jobs'][str(i)]['State'] == 'finished':
                job_ids.append(str(i))
            if len(job_ids) == n_jobs_to_get:
                break

        # Get the output form the jobs
        print "Getting files %s from %s" % (job_ids, crab_dir)
        # wish I could use the CRAB API here but doesn't like --jobids option
        # res_get = crabCommand('getoutput', crab_dir, '--jobids %s' % (','.join(job_ids)))
        crab_get_cmd = 'crab getoutput --jobids {0} {1}'.format(','.join(job_ids), crab_dir)
        print crab_get_cmd
        cmd_file.write(crab_get_cmd)
        cmd_file.write('\n')
        # subprocess.call(crab_get_cmd.split())

        # hadd the files
        # first get suitable output directory & file names
        # will put output dir in directory above this (assumes we're in L1JetEnergyCorrections/crab)
        out_dir = 'QCDPhys14_newRCT_calibrated_4'
        out_dir = crab_dir.split("/")[0].replace("l1ntuple_GCT_", "")
        out_file = 'L1Tree_QCD_Pt-50to80_Phys14_AVE30BX50_GCT_QCDPhys14_newRCT_calibrated_4.root'
        out_file = crab_dir.split("/")[1].replace("crab_", "L1Tree_")
        out_file += ".root"

        if not os.path.isdir("../"+out_dir):
            print "Making directory ../%s" % out_dir
            os.mkdir("../"+out_dir)

        output_path = "../{0}/{1}".format(out_dir, out_file)
        hadd_cmd = "hadd -f {0} {1}".format(output_path, crab_dir+"/results/L1Tree*.root")
        print hadd_cmd
        cmd_file.write(hadd_cmd)
        cmd_file.write('\n')
        # subprocess.call(hadd_cmd.split())

        # Remove the crab output files
        # os.remove(glob(crab_dir+"/results/*.root"))
        rm_cmd = 'rm {0}/results/*.root'.format(crab_dir)
        cmd_file.write(rm_cmd)
        cmd_file.write('\n')