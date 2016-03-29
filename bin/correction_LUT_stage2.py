"""Functions for printing LUTs for Stage 2

Makes 2 LUTs:

- one to convert pt to compressed index
- one to map a correction factor to each index

Gets pretty gnarly, improvements needed.
"""


import ROOT
import numpy as np
import os
import common_utils as cu
from collections import OrderedDict
from bisect import bisect_left
from multifunc import MultiFunc
import matplotlib.pyplot as plt
from binning import pairwise
from itertools import izip


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


def calc_compressed_pt_mapping(pt_orig, corr_orig, target_num_bins,
                               merge_criterion, merge_above=None, merge_below=None,
                               verbose=False):
    """Calculate new compressed pt mapping. Uses corrections
    to decide how to merge bins.
    Returns a dicts for original:quantised pt mapping.

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

    merge_above: float
        Bins above this value will be merged, ignoring merge_criterion

    merge_below: float
        Bins below this value will be merged, ignoring merge_criterion

    Returns
    -------
    new_pt_mapping: OrderedDict
        Dict of {original pt: compressed pt}, both physical pT.
    """
    print 'Calculating new mapping for compressed ET'

    # hold pt mapping
    new_pt_mapping = {p: p for p in pt_orig}
    new_pt_mapping[0] = 0.
    new_pt_mapping = OrderedDict(sorted(new_pt_mapping.items(), key=lambda t: t))

    end_ind = len(pt_orig) - 1

    if merge_above:
        merge_above_ind = 0
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            if pt >= merge_above:
                new_pt_mapping[pt] = new_pt_mapping.keys()[merge_above_ind + 1]
            else:
                merge_above_ind = ind
        end_ind = merge_above_ind

    orig_start_ind = 1

    if merge_below:
        merge_below_ind = 0
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            # keep pt = 0 set to 0
            if ind == 0:
                continue
            if pt <= merge_below:
                new_pt_mapping[pt] = new_pt_mapping.values()[1]  # we don't want 0
                merge_below_ind = ind
        orig_start_ind = merge_below_ind + 1

    last_num_bins = 111111111

    while len(set(new_pt_mapping.values())) > target_num_bins:
        last_num_bins = len(set(new_pt_mapping.values()))

        print 'Got', len(set(new_pt_mapping.values())), 'bins'
        # start with larget number of bins, look at compatibility,
        # then reduce bin span if necessary
        start_ind = orig_start_ind

        while start_ind < end_ind and end_ind > 2:
            corrs = corr_orig[start_ind: end_ind + 1]
            if corrs.max() < (merge_criterion * corrs.min()):

                # since the merge is greedy, but we want to use all our possible bins,
                # we have to modify the last group to not go over our target number
                if (end_ind < len(pt_orig) - 1 and
                    target_num_bins > (len(set(new_pt_mapping.values())) - len(corrs))):

                    start_ind += target_num_bins - (len(set(new_pt_mapping.values())) - len(corrs)) - 1
                    corrs = corr_orig[start_ind:end_ind + 1]

                if verbose:
                    print 'max:', corrs.max(), 'min:', corrs.min()
                    print 'bin edges:', start_ind, end_ind

                for i in xrange(start_ind, end_ind + 1):
                    new_pt_mapping[pt_orig[i]] = pt_orig[start_ind]

                end_ind = start_ind - 1
                if verbose: print len(set(new_pt_mapping.values())), 'diff pt values'

                break
            else:
                start_ind += 1

        if len(set(new_pt_mapping.values())) == last_num_bins:
            print 'Stuck in a loop - you need to loosen merge_criterion, or increase the numebr of bins'
            print 'Dumping mapping to file stuck_dump.txt'
            with open('stuck_dump.txt', 'w') as f:
                for k, v in new_pt_mapping.iteritems():
                    f.write("%f,%f\n" % (k, v))
            exit()

    print len(set(new_pt_mapping.values())), 'compressed bins:'
    print sorted(set(new_pt_mapping.values()))

    mask = [k != v for k, v in new_pt_mapping.iteritems()]
    if any(mask):
        # -1 required with .index() as otherwise it picks up wrong index
        print 'Quantised above (inclusive):', pt_orig[mask.index(True) - 1]
    else:
        print 'No pT quantisation happened!'
    return new_pt_mapping


def calc_new_corr_mapping(pt_orig, corr_orig, new_pt_mapping):
    """Calculate new corrections using new compressed pT mapping

    Parameters
    ----------

    Returns
    -------
    OrderedDict
        Map of {pt: new correction}
    """
    if len(pt_orig) != len(corr_orig):
        raise IndexError('Different lengths for pt_orig, corr_orig')
    # hold correction mapping
    new_corr_mapping = {p: c for p, c in zip(pt_orig, corr_orig)}
    new_corr_mapping[0] = 0.
    new_corr_mapping = OrderedDict(sorted(new_corr_mapping.items(), key=lambda t: t))

    # Get indices of locations of new pt bins
    compr_pt = list(new_pt_mapping.values())
    unique_pt = sorted(list(set(compr_pt)))  # sets are unordered!
    indices = [compr_pt.index(upt) for upt in unique_pt] + [len(corr_orig)]

    # Need to calculate new mean correction for each pt bin
    for i_low, i_high in pairwise(indices):
        mean_corr = corr_orig[i_low:i_high].mean()
        for j in xrange(i_low, i_high):
            new_corr_mapping[pt_orig[j]] = mean_corr

    return new_corr_mapping


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
    return (ieta<<4) + iet


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
    # always return factor 0 when input pt = 0
    if iet_pre == 0:
        return 0
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
        diff_below = abs(corr_matrix[ind-1, iet_pre] - iet_post)
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
    print 'Assigning HW correction factors'
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



def determine_lowest_curve_start(fit_functions):
    """Determine which fit function has the lowest pT for curve start.

    Parameters
    ----------
    fit_functions : list[MultiFunc]
        List of MultiFunc objects, one per eta bin.

    Returns
    -------
    int
        Index of MultiFunc object with curve that has lowest pT start.

    Raises
    ------
    RuntimeError
        If it picks HF bin somehow.
    """
    curve_start_pts = [f.functions_dict.keys()[0][1] for f in fit_functions]
    eta_ind_lowest = curve_start_pts.index(min(curve_start_pts))
    # make sure it's not in HF
    if eta_ind_lowest > 6:
        raise RuntimeError('Selected HF bin for pT compression')
    print 'Low pt plateaus end at:', curve_start_pts
    print 'Using eta bin %d for pT compression' % eta_ind_lowest
    return eta_ind_lowest


def assign_pt_index(pt_values):
    """Calculate an index for each pt_value. Only unique values get
    different indices.

    >>> assign_pt_index([1, 1, 2, 3, 3])
    [0, 0, 1, 2, 2]

    Parameters
    ----------
    pt_values : list[int or float]
        List of pt values

    Returns
    -------
    list[int]

    """
    pt_values = list(pt_values)
    unique_pt_values = sorted(set(pt_values))
    unique_indices_map = {p: ind for ind, p in enumerate(unique_pt_values)}
    return [unique_indices_map[p] for p in pt_values]


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

    print 'Running Stage 2 LUT making with:'
    print ' - target num pt bins (per eta bin):', target_num_pt_bins
    print ' - merge criterion:', merge_criterion
    print ' - # corr bits:', num_corr_bits
    print ' - right shift:', right_shift

    max_pt = (2**11 - 1) * 0.5

    # decide which fit func to use for binning based on which has the curve start at the lowest pT
    eta_ind_lowest = determine_lowest_curve_start(fit_functions)

    # find min of curve and merge above that
    merge_above = fit_functions[eta_ind_lowest].functions_dict.values()[1].GetMinimumX()
    print 'Merge above', merge_above

    # find end of plateau and merge below that
    merge_below = fit_functions[eta_ind_lowest].functions_dict.keys()[0][1]
    print 'Merge below', merge_below

    pt_orig = np.arange(0, max_pt + 0.5, 0.5)
    hw_pt_orig = (pt_orig * 2).astype(int)
    # do 0 separately as it should have 0 correction factor
    corr_orig = np.array([0.] + [fit_functions[eta_ind_lowest].Eval(pt) for pt in pt_orig if pt > 0])

    # Find the optimal compressed pt binning
    new_pt_mapping = calc_compressed_pt_mapping(pt_orig, corr_orig,
                                                target_num_pt_bins,
                                                merge_criterion,
                                                merge_above, merge_below)

    # print new_pt_mapping

    for ieta, func in enumerate(fit_functions):
        print 'Calculating compressed correction value for eta bin', ieta
        pt_orig = np.arange(0, max_pt + 0.5, 0.5)
        corr_orig = np.array([0.] + [func.Eval(pt) for pt in pt_orig if pt > 0.])
        new_corr_mapping = calc_new_corr_mapping(pt_orig, corr_orig, new_pt_mapping)

        title = 'Target # bins %d, merge_criterion %.3f' % (target_num_pt_bins, merge_criterion)
        plot_new_pt_corr_mapping(pt_orig, corr_orig, new_pt_mapping, new_corr_mapping, ieta, title)

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

    # plot original correction, compressed correciton, and HW correction equivalent

    # put them into a LUT
    write_stage2_correction_lut(corr_lut_filename, mapping_info, address_index_map)


def plot_new_pt_corr_mapping(pt_orig, corr_orig, new_pt_mapping, new_corr_mapping, ieta, title=''):
    """Make plots to showoff compression and mapping"""
    max_ind = -1
    # Plot original : compressed pT mapping
    plt.plot(new_pt_mapping.keys()[:max_ind], new_pt_mapping.values()[:max_ind], 'o', markersize=3, alpha=0.7)
    plt.suptitle('Compressed pt mapping, eta bin %d, %s' % (ieta, title))
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Compressed pT [GeV]')
    plt.minorticks_on()
    plt.grid(which='both')
    plt.savefig('comp_pt_map_%d.pdf' % ieta)
    plt.clf()

    # Plot original and compressed correction values as a function of pT
    plt.plot(new_corr_mapping.keys()[:max_ind], new_corr_mapping.values()[:max_ind], 'or', label='compressed', markersize=3, alpha=0.7)
    plt.plot(pt_orig[:max_ind], corr_orig[:max_ind], 'blue', label='orig')
    plt.xlabel('pT [GeV]')
    plt.ylabel('Correction')
    plt.legend(loc=0)
    plt.ylim(1, 2)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle('Compressed corr , eta bin %d, %s' % (ieta, title))
    plt.savefig('comp_corr_%d.pdf' % ieta)
    plt.xlim(10, 1000)
    plt.xscale('log')
    plt.savefig('comp_corr_logX_%d.pdf' % ieta)
    plt.clf()


def plot_pre_post_compare(map_info, corr_orig, right_shift, eta_ind):
    pt_pre = map_info['corr'].keys()
    pt_post_orig = [pt * corr for pt, corr in izip(pt_pre, corr_orig)]
    plt.plot(pt_pre, pt_post_orig, 'bo', label='Original', alpha=0.7, markersize=4)

    new_corr_map = map_info['corr']
    pt_post_compressed = [pt * corr for pt, corr in new_corr_map.iteritems()]
    plt.plot(pt_pre, pt_post_compressed, 'gd', label='Compressed', alpha=0.7, markersize=4)

    hw_corr_map = map_info['hw_corr']
    pt_post_hw = [0.5 * correct_iet(iet, cf, right_shift) for iet, cf in hw_corr_map.iteritems()]
    plt.plot(pt_pre, pt_post_hw, 'rx', label='HW', alpha=0.7, markersize=4)

    plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.xlabel('Pre-correction pT [GeV]')
    plt.ylabel('Post-correction pT [GeV]')
    plt.savefig('pt_pre_post_all_%d.pdf' % eta_ind)

    plt.xlim(0, 200)
    plt.ylim(0, 200)
    plt.savefig('pt_pre_post_all_zoom_%d.pdf' % eta_ind)

    plt.xscale('log')
    plt.yscale('log')
    plt.savefig('pt_pre_post_all_zoom_log_%d.pdf' % eta_ind)
    plt.clf()


def plot_orig_compressed_hw_corr(pt_orig, corr_orig, map_info, right_shift, eta_ind):
    plt.plot(pt_orig, corr_orig, label='Orig')
    new_corr_map = map_info['corr']
    plt.plot(new_corr_map.keys(), new_corr_map.values(), 'ro', label='Compressed', markersize=3, alpha=0.7)
    hw_corr_map = map_info['hw_corr']
    # correction factors from HW

    hw_corr_factors = [correct_iet(iet, cf, right_shift) / (1. * iet)
                       for iet, cf in hw_corr_map.iteritems() if iet > 0]
    plt.plot([x * 0.5 for x in hw_corr_map.keys() if x > 0], hw_corr_factors, 'gd', label='HW', markersize=3, alpha=0.7)
    plt.legend(loc=0)
    plt.ylim(1, 2)
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Compressed pT [GeV]')
    plt.minorticks_on()
    plt.grid(which='both')
    plt.savefig('compare_all_corr_%d.pdf' % eta_ind)

    plt.xlim(1, 1000)
    plt.xscale('log')
    plt.savefig('compare_all_corr_%d_logX.pdf' % eta_ind)


def print_Stage2_func_file(fits, output_filename):
    """Print function info to file.
    Each line corresponds to an abs(eta) bin.
    """
    with open(output_filename, 'w') as f:
        f.write('# linear constant,linear/curve physical pt boundary,curve params\n')
        num_cols = 1 + 1 + 6  # as a safeguard
        for fit in fits:
            if not fit:
                f.write('\n')
                continue
            line_cols = []
            if isinstance(fit, MultiFunc):
                linear_const = fit.functions_dict.values()[0].GetParameter(0)
                linear_limit = fit.functions_dict.keys()[0][1]
                if len(fit.functions_dict.keys()) > 1:
                    curve_fn = fit.functions_dict.values()[1]
                    curve_params = [curve_fn.GetParameter(i) for i in range(curve_fn.GetNpar())]
                else:
                    curve_params = [1, 0, 1, 0, 1, 1]  # no correction
                line_cols = [linear_const, linear_limit] + curve_params
            else:
                if "constant" in fit.GetName():
                    line_cols = [fit.GetParameter(i) for i in range(fit.GetNpar())]
                    # pad the rest with 0s (i.e. the curve part)
                    if len(line_cols) != num_cols:
                        line_cols.extend([0 for _ in range(num_cols - len(line_cols))])
                else:
                    line_cols = [fit.GetParameter(i) for i in range(fit.GetNpar())]
                    # pad the front with 0s (i.e the constant part)
                    if len(line_cols) != num_cols:
                        padding = [0 for _ in range(num_cols - len(line_cols))]
                        line_cols = padding + line_cols

            line_cols = [str(x) for x in line_cols]
            if len(line_cols) != num_cols:
                raise RuntimeError("Incorrect number of columns to write to file")
            f.write(','.join(line_cols) + '\n')


def do_constant_fit(graph, eta_min, eta_max, output_dir):
    """Do constant-value fit to graph and plot the jackknife procedure.

    We derive the constant fit value by jack-knifing. There are 2 forms here:
    - "my jackknifing": where we loop over all possible subgraphs, and calculate
    the mean for each.
    - "proper jackknifing": where we loop over all N-1 subgraphs, and calulate
    the mean for each.

    Using these, we can then find the peak mean, or the average mean.
    By default, we use the peak of "my jackknife" as it ignores the
    high-correction tail better, and gives the better-sampled low pT
    end more importance.

    Parameters
    ----------
    graph : TGraph
        Graph to fit
    eta_min, eta_max : float
        Eta bin boundaries, purely for the plots
    output_dir : str
        Output directory for plots.

    Returns
    -------
    MultiFunc
        MultiFunc object with a const-value function for the whole pT range.
    """
    print 'Doing constant-value fit'

    xarr, yarr = cu.get_xy(graph)
    xarr, yarr = np.array(xarr), np.array(yarr)  # use numpy array for easy slicing

    # "my jackknifing": Loop over all possible subgraphs, and calculate a mean for each
    end = len(yarr)
    means = []
    while end > 0:
        start = 0
        while start < end:
            means.append(yarr[start:end].mean())
            start += 1
        end -= 1

    # "proper" Jackknife means
    jack_means = [np.delete(yarr, i).mean() for i in range(len(yarr))]

    # Do plotting & peak finding, for both methods
    peak, mean = find_peak_and_average_plot(means, eta_min, eta_max,
                                            os.path.join(output_dir, 'means_hist_%g_%g_myjackknife.pdf' % (eta_min, eta_max)),
                                            'My jackknife')
    jackpeak, jackmean = find_peak_and_average_plot(jack_means, eta_min, eta_max,
                                                    os.path.join(output_dir, 'means_hist_%g_%g_root_jackknife.pdf' % (eta_min, eta_max)),
                                                    'Proper jackknife')
    print 'my jackknife peak:', peak
    print 'my jackknife mean:', mean
    print 'jackknife peak:', jackpeak
    print 'jackknfe mean:', jackmean
    const_fn = ROOT.TF1("constant", '[0]', 0, 1024)
    const_fn.SetParameter(0, peak)
    const_multifn = MultiFunc({(0, np.inf): const_fn})
    return const_multifn


def find_peak_and_average_plot(values, eta_min, eta_max, plot_filename, title='Jackknife'):
    """Plot histogram of values, and extract peak and average, using ROOT.

    Parameters
    ----------
    means: list[float]
        Collection of values
    eta_min, eta_max: float
        Eta bin edges
    plot_filename: str
        Output filepath for plot.
    title : str
        Title for plot

    Returns
    -------
    float, float
        Peak mean, and average mean.
    """
    values = np.array(values)
    # auto-generate histogram x axis limits using min/max of values + spacer
    num_bins = 75 if len(values) > 200 else 50
    hist = ROOT.TH1D('h_mean', '', num_bins, 0.95 * values.min(), 1.05 * values.max())
    for m in values:
        hist.Fill(m)
    # find peak
    peak_bin = hist.GetMaximumBin()
    peak = hist.GetBinCenter(peak_bin)
    # plot
    canv = ROOT.TCanvas('c', '', 600, 600)
    canv.SetTicks(1, 1)
    hist.Draw("HISTE")
    average = values.mean()  # average of the values
    title = '%s, %g < #eta^{L1} < %g, peak at %g, mean at %g;Subgraph mean correction' % (title, eta_min, eta_max, peak, average)
    hist.SetTitle(title)
    # Draw a marker for peak value
    arrow_peak = ROOT.TArrow(peak, 25, peak, 0)
    arrow_peak.SetLineWidth(2)
    arrow_peak.SetLineColor(ROOT.kRed)
    arrow_peak.Draw()
    # Draw a marker for average value
    arrow_mean = ROOT.TArrow(average, 5, average, 0)
    arrow_mean.SetLineWidth(2)
    arrow_mean.SetLineColor(ROOT.kBlue)
    arrow_mean.Draw()
    leg = ROOT.TLegend(0.75, 0.75, 0.88, 0.88)
    leg.AddEntry(arrow_peak, "peak", "L")
    leg.AddEntry(arrow_mean, "average", "L")
    leg.Draw()
    canv.SaveAs(plot_filename)
    return peak, average
