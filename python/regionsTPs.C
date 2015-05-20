{
    /**
     * Plot RCT regions and ECAL/HCAL trigger primitives. For debugging.
     *
     * Have to use C++ as we need the FWLite to access the objects. No PyROOT ):
     * Now compatible with ROOT6. Yuu have to forward declare any hists that you
     * Draw() to if you want to modfiy/call them later
     */
    TFile f("SimGCTEmulator_Spring15_rerunRCT_newRCT.root", "READ");
    TTree * Events = (TTree*)f.Get("Events");
    cout << Events->GetEntries() << " entries" << endl;

    TString file_app("_Spring15_newRCT");

    //////////////////////
    // Draw RCT regions //
    //////////////////////
    Events->SetAlias("caloRegions_gctDigis", "L1CaloRegions_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("caloRegions_simRctDigis", "L1CaloRegions_simRctDigis__L1NTUPLE.obj");

    Events->SetAlias("CaloEmCands_gctDigis", "L1CaloEmCands_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("CaloEmCands_simRctDigis", "L1CaloEmCands_simRctDigis__L1NTUPLE.obj");

    TCanvas * c = new TCanvas("c", "", 1400, 900);
    c->Divide(2,2);
    // 2D plot of eta vs phi, bin content = region et (from unpacker)
    c->cd(1);
    gPad->SetTicks(1,1);
    TH2F * h_gctRegions = new TH2F("h_gctRegions",";caloRegions_gctDigis.gctEta();caloRegions_gctDigis.gctPhi()", 22, 0, 22, 18, 0, 18);
    Events->Draw("L1CaloRegions_gctDigis__L1NTUPLE.obj.gctPhi():L1CaloRegions_gctDigis__L1NTUPLE.obj.gctEta()>>h_gctRegions(22,0,22,18,0,18)", "L1CaloRegions_gctDigis__L1NTUPLE.obj.et()", "COLZTEXT");

    // 2D plot of eta vs phi, bin content = region pt (from RCT emulator)
    c->cd(2);
    gPad->SetTicks(1,1);
    TH2F * h_simRctRegions = new TH2F("h_simRctRegions",";caloRegions_simRctDigis.gctEta();caloRegions_simRctDigis.gctPhi()", 22, 0, 22, 18, 0, 18);
    Events->Draw("L1CaloRegions_simRctDigis__L1NTUPLE.obj.gctPhi():L1CaloRegions_simRctDigis__L1NTUPLE.obj.gctEta()>>h_simRctRegions(22,0,22,18,0,18)", "L1CaloRegions_simRctDigis__L1NTUPLE.obj.et()", "COLZTEXT");

    // EM region rank from unpacker
    c->cd(3);
    gPad->SetTicks(1,1);
    Events->Draw("CaloEmCands_gctDigis.rank()>>h_emGct(12,0,12)", "CaloEmCands_gctDigis.rank()>0");
    // EM region rank from RCT emulator
    c->cd(4);
    gPad->SetTicks(1,1);
    Events->Draw("CaloEmCands_simRctDigis.rank()>>h_emRct(12,0,12)", "CaloEmCands_simRctDigis.rank()>0");

    c->SaveAs("regions"+file_app+".pdf");

    //////////////
    // Draw TPs //
    //////////////
    Events->SetAlias("hcalDigiTPs", "HcalTriggerPrimitiveDigisSorted_hcalDigis__L1NTUPLE.obj.obj");
    Events->SetAlias("simHcalTPs", "HcalTriggerPrimitiveDigisSorted_simHcalTriggerPrimitiveDigis__L1NTUPLE.obj.obj");
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
    TCanvas * c3 = new TCanvas("c3", "", 1800, 800);
    c3->Divide(3);
    c3->cd(1);
    gPad->SetTicks(1,1);
    TH1F * h_gct_cenJets = new TH1F("h_gct_cenJets", "GCT cen jets", 250, 0, 20000);
    TH1F * h_rct_cenJets = new TH1F("h_rct_cenJets", "GCT cen jets", 250, 0, 20000);
    Events->Draw("L1GctJetCands_simGctDigis_cenJets_L1NTUPLE.obj.raw()>>h_gct_cenJets", "L1GctJetCands_gctDigis_cenJets_L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctJetCands_simGctDigisRCT_cenJets_L1NTUPLE.obj.raw()>>h_rct_cenJets", "L1GctJetCands_simGctDigisRCT_cenJets_L1NTUPLE.obj.raw()>0");
    h_rct_cenJets->SetLineStyle(2);
    h_rct_cenJets->SetLineColor(kRed);
    h_gct_cenJets->Draw();
    h_rct_cenJets->Draw("SAME");

    c3->cd(2);
    gPad->SetTicks(1,1);
    TH1F * h_gct_fwdJets = new TH1F("h_gct_fwdJets", "GCT fwd jets", 250, 0, 20000);
    TH1F * h_rct_fwdJets = new TH1F("h_rct_fwdJets", "GCT fwd jets", 250, 0, 20000);
    Events->Draw("L1GctJetCands_simGctDigis_forJets_L1NTUPLE.obj.raw()>>h_gct_fwdJets", "L1GctJetCands_gctDigis_forJets_L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>>h_rct_fwdJets", "L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>0");
    h_rct_fwdJets->SetLineStyle(2);
    h_rct_fwdJets->SetLineColor(kRed);
    h_gct_fwdJets->Draw();
    h_rct_fwdJets->Draw("SAME");

    c3->cd(3);
    TH1F * h_gct_cenJetsIntern = new TH1F("h_gct_cenJetsIntern", "GCT cen jets internal", 250, 0, 20000);
    TH1F * h_rct_cenJetsIntern = new TH1F("h_rct_cenJetsIntern", "GCT cen jets internal", 250, 0, 20000);
    Events->Draw("L1GctInternJetDatas_simGctDigis__L1NTUPLE.obj.raw()>>h_gct_cenJetsIntern", "L1GctInternJetDatas_gctDigis__L1NTUPLE.obj.raw()>0");
    Events->Draw("L1GctInternJetDatas_simGctDigisRCT__L1NTUPLE.obj.raw()>>h_rct_cenJetsIntern", "L1GctInternJetDatas_simGctDigisRCT__L1NTUPLE.obj.raw()>0");
    h_rct_cenJetsIntern->SetLineStyle(2);
    h_rct_cenJetsIntern->SetLineColor(kRed);
    h_gct_cenJetsIntern->Draw();
    h_rct_cenJetsIntern->Draw("SAME");

    // c3->cd(4);
    // gPad->SetTicks(1,1);
    // TH1F * h_gct_fwdJetsIntern = new TH1F("h_gct_fwdJetsIntern", "GCT fwd jets internal", 250, 0, 20000);
    // TH1F * h_rct_fwdJetsIntern = new TH1F("h_rct_fwdJetsIntern", "GCT fwd jets internal", 250, 0, 20000);
    // Events->Draw("L1GctJetCands_simGctDigis_forJets_L1NTUPLE.obj.raw()>>h_gct_fwdJetsIntern", "L1GctJetCands_gctDigis_forJets_L1NTUPLE.obj.raw()>0");
    // Events->Draw("L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>>h_rct_fwdJetsIntern", "L1GctJetCands_simGctDigisRCT_forJets_L1NTUPLE.obj.raw()>0");
    // h_rct_fwdJetsIntern->SetLineStyle(2);
    // h_rct_fwdJetsIntern->SetLineColor(kRed);
    // h_gct_fwdJetsIntern->Draw();
    // h_rct_fwdJetsIntern->Draw("SAME");
    c3->SaveAs("gct_vs_rct_jets"+file_app+".pdf");

}
