import re
import sys

"""Convert tree->Scan() output to CMSSW-compatible list of events to use in PoolSource

NOTE: Scan command must have been called in this order: Scan("LumiSection:EventNumber:...")
where ... is any other fields.

Use output file:

with open(events.txt) as evt_file:
    elist = evt_file.readlines()

elist = [x.replace('\n', '') for x in elist]

Then in PoolSource:

eventsToProcess = cms.untracked.VEventRange(elist)

Or just use edmPickEvents.py --maxInteractive=30 "/ExpressPhysics/Run2015D-Express-v4/FEVT"  events.txt

ASSUMES RUN 260627!!!
"""


def make_list(filename_in, filename_out, max_num=100000000):
    run = 260627
    with open(filename_in) as fin, open(filename_out, 'w') as fout:
        i = 0
        for line in fin:
            if re.search(r'[a-z]+', line, re.IGNORECASE):
                continue

            parts = [x.strip() for x in line.split() if '*' not in x]
            if len(parts) < 3:
                continue
            if i >= max_num:
                break
            i += 1
            LS = parts[1]
            evt = parts[2]

            fout.write('%d:%s:%s\n' % (run, LS, evt))


if __name__ == "__main__":
    if len(sys.argv) == 4:
        print 'Maximum %s events' % sys.argv[3]
        make_list(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        make_list(sys.argv[1], sys.argv[2])