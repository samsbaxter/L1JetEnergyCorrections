#!/usr/bin/env python

"""
1) Get list of crappy event numbers
2) Print out maps for calo towers & jets
"""

import ROOT
import os
import sys
import glob
import random
import string


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetPalette(55)
ROOT.gStyle.SetNumberContours(512)
ROOT.gStyle.SetPaintTextFormat(".1f")
# ROOT.gStyle.SetNumberContours(100)


def random_word(length):
   return ''.join(random.choice(string.lowercase + string.uppercase) for i in range(length))


def generate_canvas(title="", width=800, height=800):
    """Generate a standard TCanvas for all plots.
    Can optionally pass in title, width and height.
    """
    c = ROOT.TCanvas("c"+random_word(5), title, width, height)
    c.SetTicks(1, 1)
    return c


def plot_jets(evt_tree, l1_upgrade_tree, reco_jet_tree, evt_num, oDir):
    evt_num = str(evt_num)
    print 'Plotting jet map for event', evt_num
    h2d_l1_jet_hw = ROOT.TH2F("h2d_l1_jet_hw_%s" % evt_num, evt_num + ' (L1Jet HW);ieta;iphi;iet', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_l1_eg_hw = ROOT.TH2F("h2d_l1_eg_hw_%s" % evt_num, evt_num + ' (EG HW);ieta;iphi;iet', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_l1_tau_hw = ROOT.TH2F("h2d_l1_tau_hw_%s" % evt_num, evt_num + ' (Tau HW);ieta;iphi;iet', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_l1_jet = ROOT.TH2F("h2d_l1_jet_%s" % evt_num, evt_num + ' (L1Jet);eta;phi;et', 120, -3, 3, 144, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
    h2d_pf_jet = ROOT.TH2F("h2d_pf_jet_%s" % evt_num, evt_num + ' (PFJet);eta;phi;et', 120, -3, 3, 144, -ROOT.TMath.Pi(), ROOT.TMath.Pi())

    c = generate_canvas()
    c.SetLogz()

    for i in xrange(tp_tree.GetEntries()):
        l1_upgrade_tree.GetEntry(i)
        pf_jet_tree.GetEntry(i)
        evt_tree.GetEntry(i)
        if int(evt_tree.Event.event) == int(evt_num):

            print 'Plotting L1 jets'
            for it in range(l1_upgrade_tree.L1Upgrade.nJets):
                h2d_l1_jet_hw.Fill(0.5 * l1_upgrade_tree.L1Upgrade.jetIEta[it], 0.5 * l1_upgrade_tree.L1Upgrade.jetIPhi[it], l1_upgrade_tree.L1Upgrade.jetIEt[it])
                h2d_l1_jet.Fill(l1_upgrade_tree.L1Upgrade.jetEta[it], l1_upgrade_tree.L1Upgrade.jetPhi[it], l1_upgrade_tree.L1Upgrade.jetEt[it])

            print 'Plotting L1 eg'
            for it in range(l1_upgrade_tree.L1Upgrade.nEGs):
                h2d_l1_eg_hw.Fill(0.5 * l1_upgrade_tree.L1Upgrade.egIEta[it], 0.5 * l1_upgrade_tree.L1Upgrade.egIPhi[it], l1_upgrade_tree.L1Upgrade.egIEt[it])

            print 'Plotting L1 taus'
            for it in range(l1_upgrade_tree.L1Upgrade.nTaus):
                # taus don't get a 0.5
                h2d_l1_tau_hw.Fill(l1_upgrade_tree.L1Upgrade.tauIEta[it], l1_upgrade_tree.L1Upgrade.tauIPhi[it], l1_upgrade_tree.L1Upgrade.tauIEt[it])

            print 'Plotting pf jets'
            for it in range(pf_jet_tree.Jet.nJets):
                h2d_pf_jet.Fill(pf_jet_tree.Jet.eta[it], pf_jet_tree.Jet.phi[it], pf_jet_tree.Jet.et[it])

            break

    if not os.path.isdir(oDir):
        os.makedirs(oDir)

    h2d_l1_jet_hw.GetZaxis().SetRangeUser(0, 512)
    h2d_l1_jet_hw.SetMarkerSize(1)
    h2d_l1_jet_hw.SetTitleOffset(1.2, 'XY')
    h2d_l1_jet_hw.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'l1_jet_hw_map.pdf'))

    h2d_l1_eg_hw.GetZaxis().SetRangeUser(0, 512)
    h2d_l1_eg_hw.SetMarkerSize(1)
    h2d_l1_eg_hw.SetTitleOffset(1.2, 'XY')
    h2d_l1_eg_hw.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'l1_eg_hw_map.pdf'))

    h2d_l1_tau_hw.GetZaxis().SetRangeUser(0, 512)
    h2d_l1_tau_hw.SetMarkerSize(1)
    h2d_l1_tau_hw.SetTitleOffset(1.2, 'XY')
    h2d_l1_tau_hw.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'l1_tau_hw_map.pdf'))

    h2d_l1_jet.GetZaxis().SetRangeUser(0, 256)
    h2d_l1_jet.SetMarkerSize(1)
    h2d_l1_jet.SetTitleOffset(1.2, 'XY')
    h2d_l1_jet.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'l1_jet_map.pdf'))

    h2d_pf_jet.GetZaxis().SetRangeUser(0, 256)
    h2d_pf_jet.SetMarkerSize(1)
    h2d_pf_jet.SetTitleOffset(1.2, 'XY')
    h2d_pf_jet.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'pf_jet_map.pdf'))


def plot_egtau(evt_tree, eg_tree, tau_tree, evt_num, oDir):
    """Plots reco eg tau"""
    evt_num = str(evt_num)
    print 'Plotting eg & tau maps for event', evt_num
    h2d_eg = ROOT.TH2F("h2d_eg_%s" % evt_num, evt_num + ' (EG);eta;phi;et', 120, -3, 3, 144, -ROOT.TMath.Pi(), ROOT.TMath.Pi())
    h2d_tau = ROOT.TH2F("h2d_tau_%s" % evt_num, evt_num + ' (Tau);eta;phi;et', 120, -3, 3, 144, -ROOT.TMath.Pi(), ROOT.TMath.Pi())

    c = generate_canvas()
    c.SetLogz()

    for i in xrange(tp_tree.GetEntries()):
        eg_tree.GetEntry(i)
        tau_tree.GetEntry(i)
        evt_tree.GetEntry(i)
        if int(evt_tree.Event.event) == int(evt_num):

            print 'Plotting eg'
            for it in range(eg_tree.Electron.nElectrons):
                h2d_eg.Fill(eg_tree.Electron.eta[it], eg_tree.Electron.phi[it], eg_tree.Electron.et[it])

            print 'Plotting taus'
            for it in range(tau_tree.Tau.nTaus):
                h2d_tau.Fill(tau_tree.Tau.eta[it], tau_tree.Tau.phi[it], tau_tree.Tau.et[it])

            break

    if not os.path.isdir(oDir):
        os.makedirs(oDir)

    h2d_eg.GetZaxis().SetRangeUser(0, 256)
    h2d_eg.SetMarkerSize(1)
    h2d_eg.SetTitleOffset(1.2, 'XY')
    h2d_eg.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'eg_map.pdf'))

    h2d_tau.GetZaxis().SetRangeUser(0, 256)
    h2d_tau.SetMarkerSize(1)
    h2d_tau.SetTitleOffset(1.2, 'XY')
    h2d_tau.Draw("COLZ TEXT")
    c.SaveAs(os.path.join(oDir, 'tau_map.pdf'))


def plot_towers(evt_tree, tp_tree, evt_num, oDir):
    evt_num = str(evt_num)
    print 'Plotting tower/tp maps for event', evt_num

    # draw the HCAL & ECAL TP maps as unpacked by hcal/ecalDigis, and l1 calo tower (which comes from layer 1 output)
    h2d_hcal = ROOT.TH2F("h2d_hcal_%s" % evt_num, evt_num + ' (HCAL TP);ieta;iphi;compEt', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_ecal = ROOT.TH2F("h2d_ecal_%s" % evt_num, evt_num + ' (ECAL TP);ieta;iphi;compEt', 83, -41.5, 41.5, 72, .5, 72.5)
    # L1 Calo Towers, from layer1Digis
    h2d_calo = ROOT.TH2F("h2d_calo_%s" % evt_num, evt_num + ' (L1CaloTower);ieta;iphi;iet', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_caloiem = ROOT.TH2F("h2d_caloiem_%s" % evt_num, evt_num + ' (L1CaloTower EM);ieta;iphi;iem', 83, -41.5, 41.5, 72, .5, 72.5)
    h2d_caloihad = ROOT.TH2F("h2d_caloihad_%s" % evt_num, evt_num + ' (L1CaloTower Had);ieta;iphi;ihad', 83, -41.5, 41.5, 72, .5, 72.5)

    c = generate_canvas()
    c.SetLogz()

    iet_max, ieta_max, iphi_max = 0, 999, 999

    for i in xrange(tp_tree.GetEntries()):
        tp_tree.GetEntry(i)
        evt_tree.GetEntry(i)
        if int(evt_tree.Event.event) == int(evt_num):
            print evt_tree.Event.lumi

            # print 'Plotting HCAL TP'
            # for it in xrange(tp_tree.CaloTP.nHCALTP):
            #     h2d_hcal.Fill(tp_tree.CaloTP.hcalTPieta[it], tp_tree.CaloTP.hcalTPCaliphi[it], tp_tree.CaloTP.hcalTPet[it])

            # print 'Plotting ECAL TP'
            # for it in range(tp_tree.CaloTP.nECALTP):
            #     h2d_ecal.Fill(tp_tree.CaloTP.ecalTPieta[it], tp_tree.CaloTP.ecalTPCaliphi[it], tp_tree.CaloTP.ecalTPcompEt[it])

            print 'Plotting Tower'
            for it in range(tp_tree.L1CaloTower.nTower):
                tow_ieta = tp_tree.L1CaloTower.ieta[it]
                tow_iphi = tp_tree.L1CaloTower.iphi[it]
                tow_iet = tp_tree.L1CaloTower.iet[it]

                h2d_calo.Fill(tow_ieta, tow_iphi, tow_iet)
                if tow_iet > iet_max:
                    iet_max, ieta_max, iphi_max = tow_iet, tow_ieta, tow_iphi
                h2d_caloiem.Fill(tow_ieta, tow_iphi, tp_tree.L1CaloTower.iem[it])
                h2d_caloihad.Fill(tow_ieta, tow_iphi, tp_tree.L1CaloTower.ihad[it])

            break

    if not os.path.isdir(oDir):
        os.makedirs(oDir)

    # h2d_hcal.GetZaxis().SetRangeUser(0, 256)
    # h2d_hcal.SetMarkerSize(0.2)
    # h2d_hcal.SetTitleOffset(1.2, 'XY')
    # h2d_hcal.Draw("COLZ TEXT")
    # draw_jet_towers(ieta_max, iphi_max)
    # c.SaveAs(os.path.join(oDir, 'hcal_map.pdf'))

    # h2d_ecal.GetZaxis().SetRangeUser(0, 512)
    # h2d_ecal.SetMarkerSize(0.2)
    # h2d_ecal.SetTitleOffset(1.2, 'XY')
    # h2d_ecal.Draw("COLZ TEXT")
    # draw_jet_towers(ieta_max, iphi_max)
    # c.SaveAs(os.path.join(oDir, 'ecal_map.pdf'))

    h2d_calo.GetZaxis().SetRangeUser(0, 512)
    h2d_calo.SetMarkerSize(0.2)
    h2d_calo.SetTitleOffset(1.2, 'XY')
    h2d_calo.Draw("COLZ TEXT")
    draw_jet_towers(ieta_max, iphi_max)
    c.SaveAs(os.path.join(oDir, 'calo_map.pdf'))

    h2d_caloiem.GetZaxis().SetRangeUser(0, 512)
    h2d_caloiem.SetMarkerSize(0.2)
    h2d_caloiem.SetTitleOffset(1.2, 'XY')
    h2d_caloiem.Draw("COLZ TEXT")
    draw_jet_towers(ieta_max, iphi_max)
    c.SaveAs(os.path.join(oDir, 'calo_iem_map.pdf'))

    h2d_caloihad.GetZaxis().SetRangeUser(0, 512)
    h2d_caloihad.SetMarkerSize(0.2)
    h2d_caloihad.SetTitleOffset(1.2, 'XY')
    h2d_caloihad.Draw("COLZ TEXT")
    draw_jet_towers(ieta_max, iphi_max)
    c.SaveAs(os.path.join(oDir, 'calo_ihad_map.pdf'))


def draw_jet_towers(ieta, iphi):
    small_box = ROOT.TBox(ieta-0.5, iphi-0.5, ieta+0.5, iphi+0.5)
    ROOT.SetOwnership(small_box, False)
    small_box.SetLineColor(ROOT.kMagenta)
    small_box.SetFillStyle(0)
    small_box.Draw()
    big_box = ROOT.TBox(ieta-4.5, iphi-4.5, ieta+4.5, iphi+4.5)
    ROOT.SetOwnership(big_box, False)
    big_box.SetLineColor(ROOT.kMagenta)
    big_box.SetFillStyle(0)
    big_box.Draw()
    left_box = ROOT.TBox(ieta-7.5, iphi-4.5, ieta-4.5, iphi+4.5)
    ROOT.SetOwnership(left_box, False)
    left_box.SetLineColor(ROOT.kMagenta)
    left_box.SetFillStyle(0)
    left_box.Draw()
    right_box = ROOT.TBox(ieta+4.5, iphi-4.5, ieta+7.5, iphi+4.5)
    ROOT.SetOwnership(right_box, False)
    right_box.SetLineColor(ROOT.kMagenta)
    right_box.SetFillStyle(0)
    right_box.Draw()
    top_box = ROOT.TBox(ieta-4.5, iphi+4.5, ieta+4.5, iphi+7.5)
    ROOT.SetOwnership(top_box, False)
    top_box.SetLineColor(ROOT.kMagenta)
    top_box.SetFillStyle(0)
    top_box.Draw()
    bottom_box = ROOT.TBox(ieta-4.5, iphi-4.5, ieta+4.5, iphi-7.5)
    ROOT.SetOwnership(bottom_box, False)
    bottom_box.SetLineColor(ROOT.kMagenta)
    bottom_box.SetFillStyle(0)
    bottom_box.Draw()


def norm_vertical_bins(hist):
    """
    Return a copy of the 2D hist, with x bin contents normalised to 1.
    This way you can clearly see the distribution per x bin,
    rather than underlying distribution across x bins.
    """

    hnew = hist.Clone(hist.GetName() + "_normX")
    nbins_y = hnew.GetNbinsY()
    for i in range(1, hnew.GetNbinsX() + 1, 1):
        y_int = hnew.Integral(i, i + 1, 1, nbins_y)
        if y_int > 0:
            scale_factor = 1. / y_int
            for j in range(1, nbins_y + 1, 1):
                hnew.SetBinContent(i, j, hist.GetBinContent(i, j) * scale_factor)
                hnew.SetBinError(i, j, hist.GetBinError(i, j) * scale_factor)
    # rescale Z axis otherwise it just removes a lot of small bins
    # set new minimum such that it includes all points, and the z axis min is
    # a negative integer power of 10
    min_bin = hnew.GetMinimum(0)
    hnew.SetAxisRange(10**math.floor(math.log10(min_bin)), 1, 'Z')
    return hnew


if __name__ == "__main__":
    l1ntuple_filename = '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_Run260627/Express/run260627_expressNoJEC.root'
    # l1ntuple_filename = '/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/L1Tree_Data_260627_noL1JEC.root'

    # pairs_filename = '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_Run260627/pairs/pairs_Express_data_ref10to5000_l10to5000_dr0p4_tightLepVeto.root'
    # pairs_filename = '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_Run260627/pairs/pairs_run260627_expressNoJEC_data_ref10to5000_l10to5000_dr0p4_noCleaning_fixedEF.root'
    pairs_filename = '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_Run260627/Express/pairs_run260627_expressNoJEC_data_ref10to5000_l10to5000_dr0p4_noCleaning_fixedEF_CSC_HLTvars.root'

    pairs_file = ROOT.TFile(pairs_filename)
    pairs_tree = pairs_file.Get("valid")

    total_dodgy_evts = 15
    dodgy_event_numbers_pefLt0p7 = []
    dodgy_event_numbers_pefGt0p7 = []
    dodgy_event_numbers_pefGt0p7_phi0or3 = []
    dodgy_event_numbers_pefGt0p7_notPhi0or3 = []
    total_good_evts = 15
    good_event_numbers = []
    dodgy_event_numbers_rsp1 = []
    dodgy_event_numbers_dphiOffset = []

    golden_lumis = []

    def clean_golden(t):
        return (t.pef<0.9
                and t.nhef < 0.9
                and t.chMult+t.nhMult+t.phMult+t.elMult+t.muMult > 1
                and t.mef < 0.8
                and t.chef > 0
                and t.chMult+t.elMult+t.muMult > 0
                and t.eef < 0.9
                and ((t.LS > 91 and t.LS < 611) or (t.LS > 613 and t.LS < 757) or (t.LS > 760 and t.LS < 788) or (t.LS > 791 and t.LS < 1051) or (t.LS > 1054 and t.LS < 1530) or (t.LS > 1533 and t.LS < 1845)))


    # Get list of event numbers
    # for event in pairs_tree:
    #     if event.pt > 150 and abs(event.eta) < 0.348 and event.ptRef < 50 and clean_golden(event) and event.muMult == 0:
    #         if event.pef < 0.7:
    #             # if len(dodgy_event_numbers_pefLt0p7) < total_dodgy_evts:
    #             dodgy_event_numbers_pefLt0p7.append(event.event)
    #         else:
    #             dodgy_event_numbers_pefGt0p7.append(event.event)
            # if not event.passCSC:
            # elif event.ptRef > 20:
                # if abs(event.phi) < 0.2 or abs(event.phi) > 3:
                    # if len(dodgy_event_numbers_pefGt0p7_phi0or3) < total_dodgy_evts:
                        # dodgy_event_numbers_pefGt0p7_phi0or3.append(event.event)
                # else:
                #     if len(dodgy_event_numbers_pefGt0p7_notPhi0or3) < total_dodgy_evts:
                #         dodgy_event_numbers_pefGt0p7_notPhi0or3.append(event.event)

        # check_lists = [dodgy_event_numbers_pefLt0p7, dodgy_event_numbers_pefGt0p7_phi0or3, dodgy_event_numbers_pefGt0p7_notPhi0or3][0:2]
        # if all(map(lambda x : len(x) == total_dodgy_evts, check_lists)):
        #     break

        # if 30 < event.ptRef < 60 and 0.8 < event.rsp < 1 and event.elMult > 0 and abs(event.eta) < 0.348 and event.passCSC and clean_golden(event):
        #     dodgy_event_numbers_rsp1.append(event.event)
        #     print event.event, event.pt, event.ptRef, event.eta, event.phi, event.deta, event.dphi

        # if len(dodgy_event_numbers_rsp1) == total_dodgy_evts:
        #     break

        # if -0.05 < event.dphi < -0.03 and abs(event.eta) < 0.348 and event.rsp < 2 and clean_golden(event) and event.muMult == 0 and event.elMult == 0 and event.ptRef > 20:
        #     dodgy_event_numbers_dphiOffset.append(event.event)
        #     print event.event, event.pt, event.ptRef, event.eta, event.phi, event.deta, event.dphi

        # if len(dodgy_event_numbers_dphiOffset) == total_dodgy_evts:
        #     break

        # if event.rsp < 1 and 280 > event.pt > 150 and 150 < event.ptRef < 250 and abs(event.eta) < 0.348 and clean_golden(event) and event.elMult == 0 and event.muMult == 0:
        #     if len(good_event_numbers) < total_good_evts:
        #         good_event_numbers.append(event.event)

        # if len(good_event_numbers) == total_good_evts:
        #     break


    # Make plots for dodgy events inside folder with event number as name
    l1ntuple_file = ROOT.TFile(l1ntuple_filename)
    event_tree = l1ntuple_file.Get('l1Tree/L1Tree')
    tp_tree = l1ntuple_file.Get('l1CaloTowerEmuTree/L1CaloTowerTree')
    l1_upgrade_tree = l1ntuple_file.Get('l1UpgradeEmuTree/L1UpgradeTree')
    pf_jet_tree = l1ntuple_file.Get('l1JetRecoTree/JetRecoTree')
    eg_tree = l1ntuple_file.Get('l1ElectronRecoTree/ElectronRecoTree')
    tau_tree = l1ntuple_file.Get('l1TauRecoTree/TauRecoTree')

    event_tree.AddFriend(tp_tree)
    event_tree.AddFriend(l1_upgrade_tree)
    event_tree.AddFriend(pf_jet_tree)
    event_tree.AddFriend(eg_tree)
    event_tree.AddFriend(tau_tree)

    # for evt_num in set(dodgy_event_numbers_pefLt0p7):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'highRsp_pefLt0p7')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'highRsp_pefLt0p7')
    #     plot_egtau(event_tree, eg_tree, tau_tree, evt_num, str(evt_num)+'highRsp_pefLt0p7')

    # for evt_num in set(dodgy_event_numbers_pefGt0p7_phi0or3):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'highRsp_pefGt0p7_phi0or3')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'highRsp_pefGt0p7_phi0or3')

    # for evt_num in set(dodgy_event_numbers_pefGt0p7_notPhi0or3):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'highRsp_pefGt0p7_notPhi0or3')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'highRsp_pefGt0p7_notPhi0or3')

    # for evt_num in set(dodgy_event_numbers_rsp1):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'rsp1_elMultGt0')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'rsp1_elMultGt0')

    # for evt_num in set(dodgy_event_numbers_dphiOffset):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'dphiOffset')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'dphiOffset')
        # plot_egtau(event_tree, eg_tree, tau_tree, evt_num, str(evt_num)+'dphiOffset')

    # for evt_num in set(good_event_numbers):
    #     plot_towers(event_tree, tp_tree, evt_num, str(evt_num)+'similarL1')
    #     plot_jets(event_tree, l1_upgrade_tree, pf_jet_tree, evt_num, str(evt_num)+'similarL1')

    # see if correlation between dodgy event nums and CSC halo list
    # -------------------------------------------------------------------------
    with open("csc2015_260627.txt") as csc_file:
        halo_evts = [int(x.split(":")[1].strip()) for x in csc_file.readlines()]

    h_pt_ptRef = ROOT.TH2F("h_pt_ptRef", ";p_{T}^{PF} [GeV];p_{T}^{L1} [GeV]", 200, 0, 400, 200, 0, 400)
    h_rsp_pt = ROOT.TH2F("h_rsp_pt", ";p_{T}^{PF} [GeV];response", 200, 0, 400, 50, 0, 5)
    h_rsp_ptRef = ROOT.TH2F("h_rsp_ptRef", ";p_{T}^{PF} [GeV];response", 200, 0, 400, 50, 0, 5)

    for i, evt in enumerate(pairs_tree):
        if i % 10000 == 0:
            print "Entry", i
        if int(evt.event) in halo_evts or not clean_golden(evt) or evt.muMult > 0 or evt.elMult>0 or abs(evt.eta) >= 0.348:
            continue
        h_pt_ptRef.Fill(evt.ptRef, evt.pt)
        # h_rsp_pt.Fill(evt.pt, evt.rsp)
        # h_rsp_ptRef.Fill(evt.ptRef, evt.rsp)

    c = generate_canvas()
    h_pt_ptRef.Draw("COLZ")
    c.SaveAs("h_pt_ptRef_clean_passCSC.pdf")

    h_rsp_pt_new = norm_vertical_bins(h_rsp_pt)
    h_rsp_pt_new.Draw("COLZ")
    c.SaveAs("h_rsp_pt_clean_passCSC.pdf")

    h_rsp_ptRef_new = norm_vertical_bins(h_rsp_ptRef)
    h_rsp_ptRef_new.Draw("COLZ")
    c.SaveAs("h_rsp_ptRef_clean_passCSC.pdf")

    # hack to convert int to long long
    # dodgy_event_numbers_pefLt0p7 = map(lambda x: int(x), dodgy_event_numbers_pefLt0p7)
    # dodgy_event_numbers_pefLt0p7 = set([x if x > 0 else x+4294967296 for x in dodgy_event_numbers_pefLt0p7])
    # dodgy_event_numbers_pefGt0p7 = map(lambda x: int(x), dodgy_event_numbers_pefGt0p7)
    # dodgy_event_numbers_pefGt0p7 = set([x if x > 0 else x+4294967296 for x in dodgy_event_numbers_pefGt0p7])

    # print "overlap (PEF < 0.7) :", set(halo_evts) & dodgy_event_numbers_pefLt0p7, 100. * len(set(halo_evts) & dodgy_event_numbers_pefLt0p7) / len(dodgy_event_numbers_pefLt0p7), '%'
    # print "overlap (PEF > 0.7) :", set(halo_evts) & dodgy_event_numbers_pefGt0p7, 100. * len(set(halo_evts) & dodgy_event_numbers_pefGt0p7) / len(dodgy_event_numbers_pefGt0p7), '%'

    pairs_file.Close()
    l1ntuple_file.Close()

