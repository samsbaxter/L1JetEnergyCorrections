#!/usr/bin/env python

"""Unit tests for Stage2 LUT maker"""


import correction_LUT_stage2 as cls
import unittest
import numpy as np
from collections import OrderedDict


class TestFunc():
    """Stand in for a TF1. All we need is Eval()"""
    def __init__(self, p0, p1, p2, p3, p4, p5):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5

    def Eval(self, et):
        part1 = self.p1 / (np.log10(et)**2 + self.p2)
        part2 = self.p3 * np.exp(-1. * self.p4 * (np.log10(et) - self.p5)**2)
        return self.p0 + part1 + part2


def check_sorted(iterable):
    return all([l <= iterable[i+1] for i, l in enumerate(iterable[:-1])])


class TestLUTMethods(unittest.TestCase):
    def setUp(self):
        """One eta bin"""
        p0, p1, p2, p3, p4, p5 = 3.18556244, 25.56760298, 2.51677342, -103.26529010, 0.00678420, -18.73657857
        self.func = TestFunc(p0, p1, p2, p3, p4, p5)
        self.max_pt = 1024
        self.target_num_pt_bins = 255
        self.merge_criterion = 1.05
        self.corr_max_hw = 511
        self.right_shift = 7

        self.pt_orig = np.arange(0.5, self.max_pt + 0.5, 0.5)
        self.corr_orig = np.array([self.func.Eval(pt) for pt in self.pt_orig])
        self.new_pt_mapping, self.new_corr_mapping = cls.calc_new_mapping(self.pt_orig,
                                                                          self.corr_orig,
                                                                          self.target_num_pt_bins,
                                                                          self.merge_criterion)
        self.mapping_info = OrderedDict()
        self.mapping_info[0] = dict(pt=self.new_pt_mapping,
                                    corr=self.new_corr_mapping,
                                    hw_corr=None,
                                    hw_corr_unique=None)

        self.address_index_map = cls.generate_address_index_map(self.mapping_info)

    def test_quantisation_mapping_zero(self):
        """Check quantised mapping has pt = 0"""
        self.assertEqual(self.new_pt_mapping.keys()[0], 0)
        self.assertEqual(self.new_pt_mapping.values()[0], 0)
        self.assertEqual(self.new_corr_mapping.keys()[0], 0)
        self.assertEqual(self.new_corr_mapping.values()[0], 0)

    def test_quantisation_size(self):
        """Check we quantise to the right number of bins"""
        self.assertEqual(len(set(self.new_pt_mapping.values())), self.target_num_pt_bins)
        self.assertEqual(len(set(self.new_corr_mapping.values())), self.target_num_pt_bins)

    def test_address_index_sorted(self):
        """Check the indices in address:index map are sorted"""
        # print self.address_index_map
        self.assertTrue(check_sorted(self.address_index_map.values()))

    def test_address_index_map_size(self):
        """Check the address:index map size and contents"""
        num_addresses = len(self.mapping_info) * ((self.max_pt * 2) + 1)
        self.assertEqual(len(self.address_index_map.keys()), num_addresses)
        num_indexes = len(self.mapping_info) * self.target_num_pt_bins
        self.assertEqual(len(set(self.address_index_map.values())), num_indexes)

    def test_address_index_map_zeros(self):
        """Check the address:index map has pt=0"""
        self.assertEqual(self.address_index_map[0], 0)

    def test_corr_matrix_size(self):
        """Check the correction matrix has the right shape"""
        rs = 7
        max_iet = 24
        max_corr = 24
        corr_m = cls.generate_corr_matrix(max_iet=max_corr, max_hw_correction=max_iet, right_shift=rs)
        self.assertEqual(corr_m.shape, (max_corr + 1, max_iet + 1))

    def test_corr_matrix(self):
        """Check the correction integer matrix is sensible"""
        rs = 7
        corr_m = cls.generate_corr_matrix(max_iet=24, max_hw_correction=32, right_shift=rs)
        corr_int = 5
        iet = 10
        answer = ((iet * corr_int)>>rs) + iet
        self.assertEqual(corr_m[corr_int][iet], answer)

    def test_correct_iet(self):
        """Check iet correction calculation works"""
        iet, corr_factor, rs = 20, 0, 7
        self.assertEqual(cls.correct_iet(iet, corr_factor, rs), ((corr_factor * iet)>>rs) + iet)

    def make_hw_corr_unique(self):
        cls.assign_hw_correction_factors(self.mapping_info, self.max_pt * 2, self.corr_max_hw, self.right_shift)

    def test_hw_corr_unique_size(self):
        """Check size of hw_corr_unique map"""
        self.make_hw_corr_unique()
        self.assertEqual(len(self.mapping_info[0]['hw_corr_unique']), self.target_num_pt_bins)

    def test_hw_corr_unique_zeros(self):
        """Check first entries are 0 in hw_corr_uniq map"""
        self.make_hw_corr_unique()
        self.assertEqual(self.mapping_info[0]['hw_corr_unique'].keys()[0], 0)
        self.assertEqual(self.mapping_info[0]['hw_corr_unique'].values()[0], 0)

    def test_hw_corr_unique_sorted(self):
        """Check keys (index) of hw_corr_unique is sorted."""
        self.make_hw_corr_unique()
        self.assertTrue(check_sorted(self.mapping_info[0]['hw_corr_unique'].keys()))

    # def test_(self):


if __name__ == '__main__':
    unittest.main()
