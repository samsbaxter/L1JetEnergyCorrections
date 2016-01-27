"""Functions for printing LUTs for Stage 2

Makes 2 LUTs:

- one to convert pt to compressed index
- one to map a correction factor to each index

Gets pretty gnarly, improvements needed.
"""


import ROOT
import sys
import array
import numpy as np
from itertools import izip
import os
import argparse
import binning
import common_utils as cu
from runCalibration import generate_eta_graph_name
from collections import OrderedDict
from bisect import bisect_left


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


def calc_new_mapping(pt_orig, corr_orig, target_num_bins, merge_criterion, verbose=False):
    """Calculate new pt/correction mappings. Returns 2 dicts,
    one for original:quantised pt mapping, and one for pt:corr mapping.

    Parameters
    ----------
    pt_orig: numpy.array
        Array of original pt bin edges (physical pT, not HW)

    corr_orig: numpy.array
        Array of original correction factors (floats, not ints)

    target_num_bins: int
        Target number of pT bins

    merge_criterion: float
        Bins will be merged if min(bins) * merge_crit > max(bins)

    Returns
    -------
    new_pt_mapping: OrderedDict
        Dict of {original pt: compressed pt}, both physical pT.

    new_corr_mapping: OrderedDict
        Dict of {original pt: correction}, where the correction value is the
        mean of the compressed bin.
    """

    # hold pt mapping
    new_pt_mapping = {p: p for p in pt_orig}
    new_pt_mapping[0] = 0.
    new_pt_mapping = OrderedDict(sorted(new_pt_mapping.items(), key=lambda t: t))

    # hold correction mapping
    new_corr_mapping = {p: c for p, c in zip(pt_orig, corr_orig)}
    new_corr_mapping[0] = 0.
    new_corr_mapping = OrderedDict(sorted(new_corr_mapping.items(), key=lambda t: t))

    end_ind = len(pt_orig) - 1

    while len(set(new_corr_mapping.values())) > target_num_bins:
        # start with larget number of bins, look at compatibility,
        # then reduce bin span if necessary
        start_ind = 0

        while start_ind < end_ind and end_ind > 2:

            corrs = corr_orig[start_ind: end_ind + 1]
            if corrs.max() < (merge_criterion * corrs.min()):

                # since the merge is greedy, but we want to use all our possible bins,
                # we have to modify the last group to not go over our target number
                if (end_ind < len(pt_orig) - 1 and
                    target_num_bins > (len(set(new_corr_mapping.values())) - len(corrs))):

                    start_ind += target_num_bins - (len(set(new_corr_mapping.values())) - len(corrs)) - 1
                    corrs = corr_orig[start_ind:end_ind + 1]

                if verbose:
                    print 'max:', corrs.max(), 'min:', corrs.min()
                    print 'bin edges:', start_ind, end_ind

                mean_corr = corrs.mean()

                for i in xrange(start_ind, end_ind + 1):
                    new_corr_mapping[pt_orig[i]] = mean_corr
                    new_pt_mapping[pt_orig[i]] = pt_orig[start_ind]

                end_ind = start_ind - 1
                if verbose: print len(set(new_corr_mapping.values())), 'diff pt values'

                break
            else:
                start_ind += 1

    mask = [k != v for k, v in new_pt_mapping.iteritems()]
    # -1 required with .index() as otherwise it picks up wrong index
    print 'Quantised above (inclusive):', pt_orig[mask.index(True) - 1]
    return new_pt_mapping, new_corr_mapping


def generate_address(iet, ieta):
    """Convert iEt, iEta to address. Must be HW values.

    Parameters
    ----------
    iet : int
        iEt value (HW)
    ieta : int
        iEta value (HW)

    Returns
    -------
    int
        Corresponding address.
    """
    return (iet<<4) + ieta


def generate_address_index_map(mapping_info):
    """Map address to index

    Parameters
    ----------
    mapping_info : TYPE
        Description
    """
    mapping = OrderedDict()
    index = -1
    for ieta, mdict in mapping_info.iteritems():
        last_pt = -1
        for pt_old, pt_new in mdict['pt'].iteritems():
            if pt_new != last_pt:
                index += 1
                last_pt = pt_new
            address = generate_address(int(pt_old * 2), ieta)
            mapping[address] = index
    return mapping


def write_pt_compress_lut(lut_filename, address_index_map):
    """Write LUT that converts pt,eta to compressed address

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    """
    print 'Making PT compress LUT', lut_filename
    with open(lut_filename, 'w') as lut:
        for i, (addr, ind) in enumerate(address_index_map.iteritems()):
            lut.write('%d %d\n' % (addr, ind))


def correct_iet(iet, corr_factor, right_shift):
    iet_new = iet * corr_factor
    iet_new = np.right_shift(iet_new, right_shift)
    iet_new += iet
    return iet_new


def generate_corr_matrix(max_iet, max_hw_correction, right_shift):
    """Generate a matrix of corrected pt values (HW), where indices are iEt
    before correction (HW) and correction integer.

    Parameters
    ----------
    max_iet: int

    max_hw_correction: int

    right_shift: int

    Returns
    -------
    numpy.ndarray:
        Correction matrix.
    """
    # corr_m[x, y] holds iet post-correction for correction factor x on iet y
    corr_m = np.ndarray(shape=(max_hw_correction + 1, max_iet + 1), dtype=int)
    for i in range(max_hw_correction + 1):
        corr_m[i] = correct_iet(np.arange(0, max_iet + 1), i, right_shift)
    return corr_m


def calculate_hw_corr_factor(corr_matrix, iet_pre, iet_post):
    """Return multiplicative factor (for hardware) that gives closest
    value to iet_post for a given iet_pre.

    Parameters
    ----------
    corr_matrix: numpy.ndarray

    iet_pre: int
        HW pt before calibration

    iet_post: int
        Target HW pt post calibration

    Returns
    -------
    int:
        Correction factor that gives closest iet_post

    """
    iet_pre = int(round(iet_pre))
    iet_post = int(round(iet_post))
    try:
        # try and find an exact match
        ind = int(np.where(corr_matrix[:, iet_pre] == iet_post)[0][0])
        return ind
    except IndexError:
        # if not, find the closest to iet_post
        ind = bisect_left(corr_matrix[:, iet_pre], iet_post)
        if ind == len(corr_matrix[:, iet_pre]):
            return ind - 1
        diff_above = abs(corr_matrix[ind, iet_pre] - iet_post)
        diff_below = abs(corr_matrix[ind, iet_pre] - iet_post)
        if diff_above < diff_below:
            return ind
        else:
            return ind - 1


def assign_hw_correction_factors(mapping_info, max_iet, cap_correction, max_hw_correction, right_shift):
    """For each pt, assign an integer correction factor

    Parameters
    ----------
    mapping_info : dict
        Description
    max_iet : int
        Description
    cap_correction : float
        Maximum physical correction (to stop ridiculously large factors)
    max_hw_correction : int
        Description
    right_shift : int
        Description
    """

    # create a correction matrix
    corr_matrix = generate_corr_matrix(max_iet, max_hw_correction, right_shift)

    # for each ieta, go though pt and convert floating-point correction factor to
    # integer factor that is used on iEt
    for ieta, mdict in mapping_info.iteritems():
        # do all pt values
        hw_corr = OrderedDict()
        for pt_pre, corr in mdict['corr'].iteritems():
            iet_pre = int(pt_pre * 2)
            iet_post = int(round(pt_pre * min(corr, cap_correction) * 2))
            hw_corr[iet_pre] = calculate_hw_corr_factor(corr_matrix, iet_pre, iet_post)
        mapping_info[ieta]['hw_corr'] = hw_corr

        # do unique value only
        hw_corr_unique = OrderedDict()
        for pt_pre in sorted(set(mdict['pt'].values())):
            iet_pre = int(pt_pre * 2)
            iet_post = int(round(pt_pre * min(mdict['corr'][pt_pre], cap_correction) * 2))
            hw_corr_unique[iet_pre] = calculate_hw_corr_factor(corr_matrix, iet_pre, iet_post)
        mapping_info[ieta]['hw_corr_unique'] = hw_corr_unique


def generate_correction_lut_contents(mapping_info, address_index_map):
    """Generate contents for Stage 2 correction LUT, for mapping index: correction factor.

    Parameters
    ----------
    mapping_info : OrderedDict
        Ordered map of {ieta : dict()}, where dict() contains dict 'hw_corr_unique'
    address_index_map : OrderedDict
        Ordered map of {address : index}

    Returns
    -------
    name : list[str]
        File contents, each entry is a line.
    """
    contents = []
    for ieta, mdict in mapping_info.iteritems():
            for iet, hw_corr in mdict['hw_corr_unique'].iteritems():
                address = generate_address(iet=iet, ieta=ieta)
                index = address_index_map[address]
                contents.append('%d %d # ieta=%d iet=%d\n' % (index, hw_corr, ieta, iet))
    return contents


def write_stage2_correction_lut(lut_filename, mapping_info, address_index_map):
    """Write LUT that converts compressed address to correction factor.

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    mapping_info : TYPE
        Description
    address_index_map : TYPE
        Description
    """
    contents = generate_correction_lut_contents(mapping_info, address_index_map)

    print 'Making corr LUT', lut_filename
    with open(lut_filename, 'w') as lut:
        for line in contents:
            lut.write(line)


def print_Stage2_lut_files(fit_functions,
                           pt_lut_filename, corr_lut_filename,
                           corr_max, num_corr_bits,
                           target_num_pt_bins, merge_criterion):
    """Make LUTs for Stage 2.

    This creates 2 LUT files:
    - one for converting (pt, eta) to an address, where pt is quantised into
    target_num_pt_bins, according to merge_criterion
    - one for mapping address to correction factor

    Parameters
    ----------
    fit_functions: list[TF1]
        List of correction functions to convert to LUT

    pt_lut_filename: str
        Filename for output LUT that converts pt, eta to compressed address

    corr_lut_filename: str
        Filename for output LUT that converts address to factor

    corr_max: float
        Maximum for correction factors. Determines the right-shift factor needed
        in hardware

    num_corr_bits: int
        Number of bits to represent correction factor.

    target_num_pt_bins: int
        Number of bins to compress pt bin range into. If you have N bits for pt,
        then target_num_pt_bins = 2**N - 1

    merge_criterion: float
        Criterion factor for compressing multiple pt bins into one bin. Bins will
        be combined if the maximum correction factor = merge_criterion * minimum
        correction factor for those pt bins.

    Raises
    ------
    IndexError
        If the number of fit functions is not the same as number of eta bins
    """
    if corr_max <= 2:
        right_shift = num_corr_bits
    elif corr_max <= 3:
        right_shift = num_corr_bits - 1
    elif corr_max <= 5:
        right_shift = num_corr_bits - 2
    elif corr_max <= 7:
        right_shift = num_corr_bits - 3
    else:
        raise RuntimeError('Correction factor > 7 sounds dangerous!')

    max_pt = 1023.5

    print 'Running Stage 2 LUT making with:'
    print ' - target num pt bins (per eta bin):', target_num_pt_bins
    print ' - merge criterion:', merge_criterion
    print ' - # corr bits:', num_corr_bits
    print ' - right shift:', right_shift
    # print ' -'

    # figure out new binning and new correction mappings, for each eta bin
    mapping_info = OrderedDict()  # store {ieta: [pt map, corr map, corr matrix]}

    for ieta, func in enumerate(fit_functions):
        pt_orig = np.arange(0.5, max_pt + 0.5, 0.5)
        corr_orig = np.array([func.Eval(pt) for pt in pt_orig])
        new_pt_mapping, new_corr_mapping = calc_new_mapping(pt_orig,
                                                            corr_orig,
                                                            target_num_pt_bins,
                                                            merge_criterion)
        mapping_info[ieta] = dict(pt=new_pt_mapping,
                                  corr=new_corr_mapping,
                                  hw_corr=None,
                                  hw_corr_unique=None)

    # map to convert address to index
    address_index_map = generate_address_index_map(mapping_info)

    # make a lut to convert original pt (address) to compressed (index)
    write_pt_compress_lut(pt_lut_filename, address_index_map)

    # then we calculate all the necessary correction integers
    assign_hw_correction_factors(mapping_info, max_iet=int(max_pt * 2), cap_correction=corr_max,
                                 max_hw_correction=(2**num_corr_bits) - 1, right_shift=right_shift)

    # put them into a LUT
    write_stage2_correction_lut(corr_lut_filename, mapping_info, address_index_map)
