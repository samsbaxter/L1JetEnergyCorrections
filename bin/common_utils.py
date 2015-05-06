"""Set of common functions that are used in loads of scripts."""

import ROOT
import os
from subprocess import call
from subprocess import check_output
from sys import platform as _platform


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
    f = ROOT.TFile(filename, mode)
    if f.IsZombie() or not f:
        raise RuntimeError("Can't open TFile %s" % filename)
    return f


def get_from_file(inFile, obj_name):
    """Get some object from ROOT TFile with checks."""
    obj = inFile.Get(obj_name)
    print "getting %s" % obj_name
    if not obj:
        raise Exception("Can't get object named %s from %s" % (obj_name, inFile.GetName()))
    return obj