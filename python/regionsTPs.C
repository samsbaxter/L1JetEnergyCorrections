void makePlots(TString filename) {
    cout << "Running over " << filename << endl;
    TFile f(filename, "READ");
    TTree * Events = (TTree*)f.Get("Events");
    cout << Events->GetEntries() << " entries" << endl;

    // auto generate an appendix for pdf names based on input file
    // Such a load of BS, why can't I just do s.Replace("SimGCTEmulator", "")?
    TString file_app = filename;
    TRegexp re("SimGCTEmulator");
    file_app(re) = "";
    TRegexp re_end(".root");
    file_app(re_end) = "";

    //////////////////////
    // Draw RCT regions //
    //////////////////////
    Events->SetAlias("caloRegions_gctDigis", "L1CaloRegions_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("caloRegions_simRctDigis", "L1CaloRegions_simRctDigis__L1NTUPLE.obj");

    Events->SetAlias("CaloEmCands_gctDigis", "L1CaloEmCands_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("CaloEmCands_simRctDigis", "L1CaloEmCands_simRctDigis__L1NTUPLE.obj");

    TCanvas * c1 = new TCanvas("c1", "", 1400, 900);
    c1->Divide(2,2);
    // L1CaloRegion: 2D plot of eta vs phi, bin content = region et (from unpacker)
    c1->cd(1);
    gPad->SetTicks(1,1);
    TH2F * h_gctRegions = new TH2F("h_gctRegions","CaloRegions from gctDigis;caloRegions_gctDigis.gctEta();caloRegions_gctDigis.gctPhi()", 22, 0, 22, 18, 0, 18);
    Events->Draw("caloRegions_gctDigis.gctPhi():caloRegions_gctDigis.gctEta()>>h_gctRegions", "caloRegions_gctDigis.et()", "COLZTEXT");

    // L1CaloRegion: 2D plot of eta vs phi, bin content = region pt (from RCT emulator)
    c1->cd(2);
    gPad->SetTicks(1,1);
    TH2F * h_simRctRegions = new TH2F("h_simRctRegions","CaloRegions from simRctDigis;caloRegions_simRctDigis.gctEta();caloRegions_simRctDigis.gctPhi()", 22, 0, 22, 18, 0, 18);
    Events->Draw("caloRegions_simRctDigis.gctPhi():caloRegions_simRctDigis.gctEta()>>h_simRctRegions", "caloRegions_simRctDigis.et()", "COLZTEXT");

    // EM region rank from unpacker
    c1->cd(3);
    gPad->SetTicks(1,1);
    TH1I * h_emGct = new TH1I("h_emGct", "CaloEmCands_gctDigis.rank();CaloEmCands_gctDigis.rank();", 12, 0, 12);
    Events->Draw("CaloEmCands_gctDigis.rank()>>h_emGct(12,0,12)", "CaloEmCands_gctDigis.rank()>0");
    // EM region rank from RCT emulator
    c1->cd(4);
    gPad->SetTicks(1,1);
    TH1I * h_emRct = new TH1I("h_emRct", "CaloEmCands_simRctDigis.rank();CaloEmCands_simRctDigis.rank();", 12, 0, 12);
    Events->Draw("CaloEmCands_simRctDigis.rank()>>h_emRct(12,0,12)", "CaloEmCands_simRctDigis.rank()>0");

    c1->SaveAs("regions"+file_app+".pdf");

    //////////////
    // Draw TPs //
    //////////////
    Events->SetAlias("simHcalTPs", "HcalTriggerPrimitiveDigisSorted_simHcalTriggerPrimitiveDigis__L1NTUPLE.obj.obj");
    Events->SetAlias("hcalDigiTPs", "HcalTriggerPrimitiveDigisSorted_hcalDigis__L1NTUPLE.obj.obj");
    Events->SetAlias("ecalTPs", "EcalTriggerPrimitiveDigisSorted_ecalDigis_EcalTriggerPrimitives_L1NTUPLE.obj.obj");

    TCanvas * c2 = new TCanvas("c2", "", 1400, 900);
    c2->Divide(2,2);
    // HCAL TPs et
    c2->cd(1);
    TH1F * h_simHcalEt = new TH1F("h_simHcalEt", "HcalTPs.SOI_compressedEt()", 32, 0,32);
    TH1F * h_hcalDigiEt = new TH1F("h_hcalDigiEt", "HcalTPs.SOI_compressedEt()", 32, 0,32);
    Events->Draw("simHcalTPs.SOI_compressedEt()>>h_simHcalEt", "simHcalTPs.SOI_compressedEt()>0");
    Events->Draw("hcalDigiTPs.SOI_compressedEt()>>h_hcalDigiEt", "hcalDigiTPs.SOI_compressedEt()>0");
    h_hcalDigiEt->SetLineStyle(2);
    h_hcalDigiEt->SetLineColor(kRed);
    h_simHcalEt->Draw();
    h_hcalDigiEt->Draw("SAME");
    TLegend l_hcal(0.5, 0.6, 0.88, 0.88);
    l_hcal.AddEntry(h_hcalDigiEt, "HCAL TPs from hcalDigis", "L");
    l_hcal.AddEntry(h_simHcalEt, "HCAL TPs from simHcalTriggerPrimitiveDigis", "L");
    l_hcal.Draw();

    // HCAL TPs, eta vs phi, bin content = et
    c2->cd(2);
    gPad->SetTicks(1,1);
    TH2F * h_hcaltps = new TH2F("h_hcaltps", ";simHcalTPs.id().ieta();simHcalTPs.id().iphi()", 64, -32, 32, 72, 0, 72);
    Events->Draw("simHcalTPs.id().iphi():simHcalTPs.id().ieta()>>h_hcaltps", "simHcalTPs.SOI_compressedEt()", "COLZTEXT");

    // ECAL TPs et
    c2->cd(3);
    TH1I * ecalTPet = new TH1I("h_ecalTPet", "ecalTPs.compressedEt()", 32, 0, 32);
    Events->Draw("ecalTPs.compressedEt()>>h_ecalTPet", "ecalTPs.compressedEt()>0");

    // ECAL Tps,e ta vs phi, bin content = et
    c2->cd(4);
    gPad->SetTicks(1,1);
    TH2F * h_ecaltps = new TH2F("h_ecaltps", ";ecalTPs.id().ieta();ecalTPs.id().iphi()", 64, -32, 32, 72, 0, 72);
    Events->Draw("ecalTPs.id().iphi():ecalTPs.id().ieta()>>h_ecaltps", "ecalTPs.compressedEt()", "COLZTEXT");
    c2->SaveAs("HcalEcalTP"+file_app+".pdf");

    //////////////////
    // Compare jets //
    //////////////////
    TCanvas * c3 = new TCanvas("c3", "", 1800, 600);
    c3->Divide(3);

    // GCT cenJets
    c3->cd(1);
    gPad->SetTicks(1,1);
    TH1F * h_gct_cenJets = new TH1F("h_gct_cenJets", "GCT cen jets;jet.raw();", 250, 0, 20000);
    TH1F * h_rct_cenJets = new TH1F("h_rct_cenJets", "GCT cen jets;jet.raw();", 250, 0, 20000);
    Events->Draw("L1GctJetCands_simGctDigis_cenJets_L1NTUPLE.obj.raw()>>h_gct_cenJets", "L1GctJetCands_simGctDigis_cenJets_L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctJetCands_simGctDigisRCT_cenJets_L1NTUPLE.obj.raw()>>h_rct_cenJets", "L1GctJetCands_simGctDigisRCT_cenJets_L1NTUPLE.obj.raw()>0");
    h_rct_cenJets->SetLineStyle(2);
    h_rct_cenJets->SetLineColor(kRed);
    h_gct_cenJets->Draw();
    h_rct_cenJets->Draw("SAME");
    TLegend l_jets(0.5, 0.8, 1, 0.9);
    l_jets.AddEntry(h_gct_cenJets, "GCT jets using regions from unpacker", "L");
    l_jets.AddEntry(h_rct_cenJets, "GCT jets using regions from simRctDigis", "L");
    l_jets.Draw();

    // GCT fwdJets
    c3->cd(2);
    gPad->SetTicks(1,1);
    TH1F * h_gct_fwdJets = new TH1F("h_gct_fwdJets", "GCT fwd jets;jet.raw();", 250, 0, 20000);
    TH1F * h_rct_fwdJets = new TH1F("h_rct_fwdJets", "GCT fwd jets;jet.raw();", 250, 0, 20000);
    Events->Draw("L1GctJetCands_simGctDigis_forJets_L1NTUPLE.obj.raw()>>h_gct_fwdJets", "L1GctJetCands_simGctDigis_forJets_L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>>h_rct_fwdJets", "L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>0");
    h_rct_fwdJets->SetLineStyle(2);
    h_rct_fwdJets->SetLineColor(kRed);
    h_gct_fwdJets->Draw();
    h_rct_fwdJets->Draw("SAME");
    l_jets.Draw();

    // GCT Internal jets
    c3->cd(3);
    gPad->SetLogy();
    TH1F * h_gct_cenJetsIntern = new TH1F("h_gct_cenJetsIntern", "GCT internal jets;jet.raw();", 250, 0, 12000000);
    TH1F * h_rct_cenJetsIntern = new TH1F("h_rct_cenJetsIntern", "GCT internal jets;jet.raw();", 250, 0, 12000000);
    Events->Draw("L1GctInternJetDatas_simGctDigis__L1NTUPLE.obj.raw()>>h_gct_cenJetsIntern", "L1GctInternJetDatas_simGctDigis__L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctInternJetDatas_simGctDigisRCT__L1NTUPLE.obj.raw()>>h_rct_cenJetsIntern", "L1GctInternJetDatas_simGctDigisRCT__L1NTUPLE.obj.raw()>0");
    h_rct_cenJetsIntern->SetLineStyle(2);
    h_rct_cenJetsIntern->SetLineColor(kRed);
    h_gct_cenJetsIntern->Draw();
    h_rct_cenJetsIntern->Draw("SAME");
    l_jets.Draw();

    c3->SaveAs("gct_vs_rct_jets"+file_app+".pdf");

    f.Close();
    delete c1;
    delete c2;
    delete c3;
}

void regionsTPs() {
    /**
     * Plot RCT regions, ECAL/HCAL trigger primitives, and GCT jets. For debugging.
     *
     * Have to use C++ as we need the FWLite to access the objects. No PyROOT ):
     * Now compatible with ROOT6. You have to forward declare any hists that you
     * Draw() to if you want to modfiy/call them later (didn't have to in ROOT5)
     */

    // EDM input filename(s)
    // TString filename("SimGCTEmulator_Spring15_caloStage1RCTLuts_default_rerunRCT.root");
    // TString filename("SimGCTEmulator_Spring15_default_rerunRCT.root");
    // TString filename("SimGCTEmulator_Spring15_rerunRCT_newRCT.root");

    // Note: this will almost certainly not work in ROOT5, given it uses a templated obj.
    std::vector<TString> filenames;
    filenames.push_back("SimGCTEmulator_Spring15_caloStage1RCTLuts_default_rerunRCT.root");
    filenames.push_back("SimGCTEmulator_Spring15_default_rerunRCT.root");
    filenames.push_back("SimGCTEmulator_Spring15_rerunRCT_newRCT.root");

    for (int i = 0; i < filenames.size(); i++){
        makePlots(filenames.at(i));
    }
}


