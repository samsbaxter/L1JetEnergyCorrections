"""
Helper functions for HTCondor submit scripts
"""


import os
from subprocess import call
import random
import string


def update_setup_script(setup_script, cmssw_ver, root_dir):
    """Update condor setup script with correct CMSSW version and ROOT dir.

    setup_script: str
        Filename for condor worker script
    cmssw_ver: str
        CMSSW version
    root_dir: str
        Directory for ROOT. Must contain bin/thisroot.sh
    """
    sed_cmds = ['sed -i s/VER=CMSSW_.*/VER=%s/ %s' % (cmssw_ver, setup_script),
                'sed -i s@RDIR=/.*@RDIR=%s@ %s' % (root_dir, setup_script)]
    for cmd in sed_cmds:
        call(cmd.split())


def update_hadd_setup_script(hadd_setup_script, cmssw_ver):
    """Update condor hadd worker script with correct CMSSW version and ROOT dir.

    hadd_setup_script: str
        Filename for condor hadd worker script
    cmssw_ver: str
        CMSSW version
    """
    sed_cmd = 'sed -i s/VER=CMSSW_.*/VER=%s/ %s' % (cmssw_ver, hadd_setup_script)
    call(sed_cmd.split())


def check_file_exists(filename):
    """Check if file exists, if not raise error."""
    if not os.path.isfile(filename):
        raise OSError('%s does not exist!' % filename)


def check_create_dir(directory, info=False):
    """Check dir exists, if not create"""
    if not os.path.isdir(directory):
        if os.path.isfile(directory):
            raise RuntimeError('%s already exists as a file' % directory)
        # os.makedirs(directory) # can no longer use normal bash commands on /hdfs
        hadoopDirectory = directory[5:] # strips off the /hdfs prefix
        os.system("hadoop fs -mkdir %s" % hadoopDirectory)
        if info:
            print 'Making dir', directory


def rand_str(length=3):
    """Generate a random string of user-specified length"""
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase)
                   for _ in range(length))
