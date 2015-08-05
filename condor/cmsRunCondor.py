#!/usr/bin/env python

"""
Script to allow you to run cmsRun jobs on HTCondor.

Bit rudimentary. See options with:

cmsRunCondor.py --help

Note that it automatically sets the correct process.source, and process.maxEvents

Robin Aggleton 2015, in a rush
"""


import sys
import argparse
import os
from time import strftime
import subprocess
import re
import math
import logging


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


def main(in_args):

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="CMSSW config file you want to run.")
    parser.add_argument("--outputDir", help="Where you want your output to be stored. /hdfs is recommended")
    parser.add_argument("--dataset", help="Name of dataset you want to run over")
    parser.add_argument("--filesPerJob", help="Number of files to run over, per job.", type=int, default=5)
    parser.add_argument("--totalFiles", help="Total number of files to run over. Default is ALL (-1)", type=int, default=-1)
    parser.add_argument("--verbose", help="Extra printout to clog up your screen.", action='store_true')
    args = parser.parse_args(args=in_args)

    if args.verbose:
        log.setLevel(logging.DEBUG)

    # do some checking
    if not os.path.isfile(args.config):
        log.error("Cannot find config file %s" % args.config)
        raise IOError

    if not os.path.exists(args.outputDir):
        print "Output directory doesn't exists, trying to make it:", args.outputDir
        try:
            os.mkdir(args.outputDir)
        except OSError as e:
            log.error("Cannot make output dir %s" % args.outputDir)
            raise

    if args.filesPerJob > args.totalFiles and args.totalFiles != -1:
        log.error("You can't have --filesPerJob > --totalFiles!")
        raise RuntimeError

    # make an output directory for log files
    if not os.path.exists(args.outputDir):
        os.mkdir('jobs')

    # get the total number of files for this dataset using das_client
    output = subprocess.check_output(['das_client.py','--query', 'summary dataset=%s' % args.dataset], stderr=subprocess.STDOUT)
    log.debug(output)
    total_num_files = int(re.search(r'nfiles +: (\d*)', output).group(1))

    if args.totalFiles == -1:
        args.totalFiles = total_num_files

    # Figure out correct numebr of jobs
    total_num_jobs = int(math.ceil(args.totalFiles / float(args.filesPerJob)))

    log.debug("Will be submitting %d jobs, running over %d files" % (total_num_jobs, args.totalFiles))

    # Make a condor submission script
    with open('cmsRun_template.condor') as template:
        job_template = template.read()

    config_filename = os.path.basename(args.config)
    job_filename = '%s_%s.condor' % (config_filename.replace(".py", ""), strftime("%H%M%S"))

    # job_description = job_template.replace("SEDINITIAL", args.outputDir)
    job_description = job_template.replace("SEDINITIAL", "")  # for not, keept initialdir local, otherwise tonnes of files on hdfs
    job_description = job_description.replace("SEDNAME", job_filename.replace(".condor", ""))
    args_str = "%s %s %d %d %s $(process)" % (config_filename, args.dataset, args.filesPerJob, args.totalFiles, args.outputDir)
    job_description = job_description.replace("SEDARGS", args_str)
    job_description = job_description.replace("SEDEXE", 'cmsRun_worker.sh')
    job_description = job_description.replace("SEDNJOBS", str(total_num_jobs))
    job_description = job_description.replace("SEDINPUTFILES", os.path.abspath(args.config))

    with open(job_filename, 'w') as submit_script:
        submit_script.write(job_description)
    log.info('New condor submission script written to %s' % job_filename)


if __name__ == "__main__":
    main(sys.argv[1:])