#!/usr/bin/env python
"""
Run cmsRun job on HTCondor, for faster testing.

Just edit CONFIG, LOG_DIR, OUT_DIR.

Designed for small runs, not large ones!!!
"""


from time import strftime
import importlib
import htcondenser as ht
import os


CONFIG = 'ntuple_maker_SMReco.py'

LOG_DIR = '/storage/%s/CMSSW/%s' % (os.environ['LOGNAME'], strftime("%d_%b_%y"))

OUT_DIR = '/hdfs/user/%s' % (os.environ['LOGNAME'])


if __name__ == "__main__":
    # Get output ntuple file from config file
    config = importlib.import_module(os.path.splitext(CONFIG)[0])
    output_file = config.process.TFileService.fileName.value()
    print 'Output file:', output_file

    # Create job
    job_set = ht.JobSet(exe='cmsRun', copy_exe=False, certificate=True,
                        out_dir=LOG_DIR, err_dir=LOG_DIR, log_dir=LOG_DIR,
                        cpus=1, memory='200MB', disk='200MB',
                        hdfs_store=OUT_DIR, filename='cmsRun.condor')
    job = ht.Job(name='cmsRunJob', args=[CONFIG], input_files=[CONFIG],
                 output_files=[output_file], hdfs_mirror_dir=OUT_DIR)
    job_set.add_job(job)
    job_set.submit()
