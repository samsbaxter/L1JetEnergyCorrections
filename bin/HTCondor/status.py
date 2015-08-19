"""
Code to interpret a DAGman status output, and present it in a more user-friendly manner.
"""


import sys
import logging
from pprint import pprint
import re
import os
from collections import OrderedDict


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


def strip_doublequotes(string):
    return re.search(r'\"(.*)\"', string).group(1)


class ClassAd(object):
    def __init__(self):
        pass


class DagStatus(ClassAd):
    def __init__(self, timestamp, dag_status, nodes_total, nodes_done,
                 nodes_pre, nodes_queued, nodes_post, nodes_ready,
                 nodes_unready, nodes_failed, job_procs_held, job_procs_idle):
        self.timestamp = timestamp
        self.dag_status = strip_doublequotes(dag_status)
        self.nodes_total = int(nodes_total)
        self.nodes_done = int(nodes_done)
        self.nodes_pre = int(nodes_pre)
        self.nodes_queued = int(nodes_queued)
        self.nodes_post = int(nodes_post)
        self.nodes_ready = int(nodes_ready)
        self.nodes_unready = int(nodes_unready)
        self.nodes_failed = int(nodes_failed)
        self.job_procs_held = int(job_procs_held)
        self.job_procs_idle = int(job_procs_idle)


class NodeStatus(ClassAd):
    def __init__(self, node, node_status, status_details, retry_count,
                 job_procs_queued, job_procs_held):
        self.node = strip_doublequotes(node)
        self.node_status = strip_doublequotes(node_status)
        self.status_details = status_details
        self.retry_count = int(retry_count)
        self.job_procs_queued = int(job_procs_queued)
        self.job_procs_held = int(job_procs_held)


class StatusEnd(ClassAd):
    def __init__(self, end_time, next_update):
        self.end_time = strip_doublequotes(end_time)
        self.next_update = strip_doublequotes(next_update)


def process(status_filename):
    """Main function to process the status file"""

    dag_status = None
    node_statuses = []
    status_end = None

    with open(status_filename) as sfile:
        contents = {}
        store_contents = False
        for line in sfile:
            if line.startswith("[") or "}" in line:
                store_contents = True
                continue
            elif line.startswith("]"):
                log.debug(contents)
                # do something with contents here, depending on Type key
                if contents['Type'] == '"DagStatus"':
                    dag_status = DagStatus(timestamp=contents['Timestamp'],
                                           dag_status=contents['DagStatus'],
                                           nodes_total=contents['NodesTotal'],
                                           nodes_done=contents['NodesDone'],
                                           nodes_pre=contents['NodesPre'],
                                           nodes_queued=contents['NodesQueued'],
                                           nodes_post=contents['NodesPost'],
                                           nodes_ready=contents['NodesReady'],
                                           nodes_unready=contents['NodesUnready'],
                                           nodes_failed=contents['NodesFailed'],
                                           job_procs_held=contents['JobProcsHeld'],
                                           job_procs_idle=contents['JobProcsIdle'])
                elif contents['Type'] == '"NodeStatus"':
                    node = NodeStatus(node=contents['Node'],
                                      node_status=contents['NodeStatus'],
                                      status_details=contents['StatusDetails'],
                                      retry_count=contents['RetryCount'],
                                      job_procs_queued=contents['JobProcsQueued'],
                                      job_procs_held=contents['JobProcsHeld'])
                    node_statuses.append(node)
                elif contents['Type'] == '"StatusEnd"':
                    status_end = StatusEnd(end_time=contents['EndTime'],
                                           next_update=contents['NextUpdate'])
                else:
                    print contents['Type']
                    raise KeyError("Unknown block Type")
                contents = {}
                store_contents = False
                continue
            elif "{" in line:
                store_contents = False
                continue
            elif store_contents:
                line = line.replace("\n", "").replace(";", "").strip()
                parts = line.split(" = ")
                contents[parts[0]] = parts[1]

    print_table(dag_status, node_statuses, status_end)


def print_table(dag_status, node_statuses, status_end):
    """Print a pretty-ish table with important info

    TODO: auto-size the columns. Use terminal window width?
    """
    # rows, columns = os.popen('stty size', 'r').read().split()
    # rows = int(rows)
    # columns = int(int(columns)*0.75)
    columns = 80

    # Print info for each job.
    job_dict = OrderedDict()  # holds column title as key and object attribute name as value
    job_dict["Node"] = "node"
    job_dict["Status"] = "node_status"
    job_dict["Retries"] = "retry_count"

    # Auto-size each column
    job_col_widths = [max(max(len(str(x.__dict__[v])) for x in node_statuses), len(k)) for k, v in job_dict.iteritems()]

    print "*" * columns
    # make formatter string to be used for each row, auto calculates number of columns
    job_format = " | ".join(["{{:<{}}}"]*len(job_dict.keys())).format(*job_col_widths)
    print job_format.format(*job_dict.keys())
    print "-" * columns
    for n in node_statuses:
        print job_format.format(*[n.node, n.node_status, n.retry_count])
    print "*" * columns

    # print summary of all jobs
    labels = ['DAG status', 'Total', 'Queued', 'Ready', 'Failed', 'Done']
    print "{:<25} | {:<7} | {:<7} | {:<7} | {:<7} | {:<7}".format(*labels)
    print "-" * columns
    entries = [dag_status.dag_status, dag_status.nodes_total,
               dag_status.nodes_queued, dag_status.nodes_ready,
               dag_status.nodes_failed, dag_status.nodes_done,
               100. * dag_status.nodes_done / dag_status.nodes_total]
    print "{:<25} | {:<7} | {:<7} | {:<7} | {:<7} | {:<4} ({:4.1f}%)".format(*entries)
    print "*" * columns

    # print time of next update
    print "Status recorded at:", status_end.end_time
    print "Next update:       ", status_end.next_update
    print "*" * columns


if __name__ == "__main__":
    process(sys.argv[1])
