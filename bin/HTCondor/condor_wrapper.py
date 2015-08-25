#!/usr/bin/env python

"""
Wrapper for python code to run on condor.

We can't just execute the command on condor - we have to intervene in 2 ways:

1) it's best to copy the input file from /hdfs to the local worker node.
This avoids several processes trying to access the same file simultaneously
(whish is mayhem in ROOT).

2) you cannot stream the outut to /hdfs. Instead we write to a local file and
then copy it across afterwards.

So to avoid the user having to worry about those things, we take as arguments:

condor_wrapper.py <input file> <output file> <full command>

and this will automate the above.
"""

import os
import sys
import re
import subprocess
import argparse
import random, string

print "condor_wrapper, innit"
print sys.argv
parser = argparse.ArgumentParser()
parser.add_argument("input", help="input filename")
parser.add_argument("output", help="output filename")
parser.add_argument("command", help="command that you would run e.g. python runCalibration.py pairs.root output.root", nargs=argparse.REMAINDER)
args = parser.parse_args()

print args
outputname = ""
# make unique output filename in case 2 jobs run on same node
random_str = ''.join(random.choice(string.lowercase) for i in xrange(3))
tmpname = "temp_%s.root" % (random_str)

commands = args.command
for i, opt in enumerate(commands):
    if re.match(r"/hdfs/user/ra12451/L1JEC/CMSSW_\d_\d_.*/src/L1Trigger/L1JetEnergyCorrections/.*/%s.*" % args.filestem, opt):
        outputname = opt
        print opt
        commands[i] = tmpname

# Actaully call the commands
print ' '.join(commands)
subprocess.call(commands)

# Copy across to HDFS
cmd = "hadoop fs -copyFromLocal -f %s %s" % (tmpname, outputname.replace("/hdfs", ""))
print cmd
subprocess.call(cmd.split())

# Remove the temp file
os.remove(tmpname)