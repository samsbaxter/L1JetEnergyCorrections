"""Set of common functions that are used in loads of scripts."""

import ROOT
import os
from subprocess import call
from subprocess import check_output
from sys import platform as _platform
import numpy as np


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.TH1.SetDefaultSumw2(True)


def open_pdf(pdf_filename):
    """Open a PDF file using system's default PDF viewer."""
    if _platform.startswith("linux"):
        # linux
        call(["xdg-open", pdf_filename])
    elif _platform == "darwin":
        # OS X
        call(["open", pdf_filename])
    elif _platform == "win32":
        # Windows
        call(["start", pdf_filename])

#
# Filepath/directory fns
#
def cleanup_filepath(filepath):
    """Resolve any env vars, ~, etc, and return absolute path."""
    return os.path.abspath(os.path.expandvars(os.path.expanduser(filepath)))


def get_full_path(filepath):
    """Return absolute directory of filepath.
    Resolve any environment vars, ~, sym links(?)"""
    return os.path.dirname(cleanup_filepath(filepath))


def check_file_exists(filepath):
    """Check if file exists. Can do absolute or relative file paths."""
    return os.path.isfile(cleanup_filepath(filepath))


def check_dir_exists(filepath):
    """Check if directory exists."""
    return os.path.isdir(cleanup_filepath(filepath))


def check_dir_exists_create(filepath):
    """Check if directory exists. If not, create it."""
    if not check_dir_exists(filepath):
        os.makedirs(cleanup_filepath(filepath))

#
# ROOT specific fns, like openign files safely
#
def open_root_file(filename, mode="READ"):
    """Safe way to open ROOT file. Could be improved."""
    if not check_file_exists(filename):
        raise RuntimeError("No such file %s" % filename)
    f = ROOT.TFile(filename, mode)
    if f.IsZombie() or not f:
        raise RuntimeError("Can't open TFile %s" % filename)
    return f


def exists_in_file(tfile, obj_name):
    """Check if object exists in TFile.

    Also handles directory structure, e.g. histograms/central/pt_1
    """
    parts = obj_name.split("/")
    current_obj = tfile
    for p in parts:
        if current_obj.GetListOfKeys().Contains(p):
            current_obj = current_obj.Get(p)
        else:
            return False
    return True


def get_from_file(tfile, obj_name):
    """Get some object from ROOT TFile with checks."""
    print "getting %s" % obj_name
    if not exists_in_file(tfile, obj_name):
        raise Exception("Can't get object named %s from %s" % (obj_name, tfile.GetName()))
    else:
        return tfile.Get(obj_name)


def check_exp(n):
    """
    Checks if number has stupidly larger exponent

    Can occur is using buffers - it just fills unused bins with crap
    """

    from math import fabs, log10, frexp
    m,e = frexp(n)
    return fabs(log10(pow(2,e))) < 10


def get_xy(graph):
    """
    Return lists of x, y points from a graph, because it's such a PITA

    ASSUMES POINTS START FROM INDEX 0!
    Includes a check to see if any number is ridic (eg if you started from 1)
    """
    xpt = graph.GetX()
    ypt = graph.GetY()
    N = graph.GetN()

    xarr = [x for x in list(np.ndarray(N,'d',xpt)) if check_exp(x)]
    yarr = [y for y in list(np.ndarray(N,'d',ypt)) if check_exp(y)]

    if len(xarr) != N or len(yarr) != N:
        raise Exception("incorrect array size from graph")

    return xarr, yarr


def get_exey(graph):
    """
    Return lists of errors on x, y points from a graph, because it's such a PITA

    ASSUMES POINTS START FROM INDEX 0!
    Includes a check to see if any number is ridic (eg if you started from 1)
    """
    expt = graph.GetEX()
    eypt = graph.GetEY()
    N = graph.GetN()

    xarr = [x for x in list(np.ndarray(N,'d',expt)) if check_exp(x)]
    yarr = [y for y in list(np.ndarray(N,'d',eypt)) if check_exp(y)]

    if len(xarr) != N or len(yarr) != N:
        raise Exception("incorrect array size from graph")

    return xarr, yarr

