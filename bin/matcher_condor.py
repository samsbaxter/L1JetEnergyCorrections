"""
Script to run RunMatcher on worker node of HTCondor.

Since we can't write to /hdfs but do want to eventually store files there,
we need to manipulate the user's args to pull the specified output file,
replace it with our own, then copy the local output to wherever the user specified.
"""

#!/usr/bin/env python

import sys
from subprocess import call

# Grab user-defined output filename and replace it with some temp filename
in_args = sys.argv[1:]
outfile = ''

ind1 = 0
for i, p in enumerate(in_args):
    if p == '-O' or p == '--output':
        outfile = in_args[i+1]
        ind1 = i
        break

tmp_filename = 'pairs_tmp.root'
if ind1 or outfile != '':
    in_args[ind1+1] = tmp_filename

# Run RunMatcher with all other args
print in_args
call(in_args)

# once finished move temp file to hdfs
cp_cmds = 'cp %s %s' % (tmp_filename, outfile)
print cp_cmds
call(cp_cmds.split())