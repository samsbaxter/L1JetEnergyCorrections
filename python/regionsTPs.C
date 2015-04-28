{
    /**
     * Plot RCT regions and ECAL/HCAL trigger primitives. For debugging.
     */
    TFile f("SimGCTEmulator_hcalRecAlgos.root");

    // Draw RCT regions
    Events->SetAlias("caloRegions_gctDigis", "L1CaloRegions_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("caloRegions_simRctDigis", "L1CaloRegions_simRctDigis__L1NTUPLE.obj");

    Events->SetAlias("CaloEmCands_gctDigis", "L1CaloEmCands_gctDigis__L1NTUPLE.obj");
    Events->SetAlias("CaloEmCands_simRctDigis", "L1CaloEmCands_simRctDigis__L1NTUPLE.obj");
    TCanvas * c = new TCanvas("c", "", 1400, 900);
    c->Divide(2,2);
    c->cd(1);
    gPad->SetTicks(1,1);
    Events->Draw("caloRegions_gctDigis.gctPhi():caloRegions_gctDigis.gctEta()>>h_gctRegions(22,0,22,18,0,18)", "caloRegions_gctDigis.et()", "COLZTEXT");
    h_gctRegions->SetTitle(";caloRegions_gctDigis.gctEta();caloRegions_gctDigis.gctPhi()");
    c->cd(2);
    gPad->SetTicks(1,1);
    Events->Draw("caloRegions_simRctDigis.gctPhi():caloRegions_simRctDigis.gctEta()>>h_simRctRegions(22,0,22,18,0,18)", "caloRegions_simRctDigis.et()", "COLZTEXT");
    h_simRctRegions->SetTitle(";caloRegions_simRctDigis.gctEta();caloRegions_simRctDigis.gctPhi()");
    c->cd(3);
    gPad->SetTicks(1,1);
    Events->Draw("CaloEmCands_gctDigis.rank()", "CaloEmCands_gctDigis.rank()>0");
    c->cd(4);
    gPad->SetTicks(1,1);
    Events->Draw("CaloEmCands_simRctDigis.rank()", "CaloEmCands_simRctDigis.rank()>0");
    c->SaveAs("regions.pdf");

    // Draw TPs
    Events->SetAlias("simHcalTPs", "HcalTriggerPrimitiveDigisSorted_simHcalTriggerPrimitiveDigis__L1NTUPLE.obj.obj");
    Events->SetAlias("ecalTPs", "EcalTriggerPrimitiveDigisSorted_ecalDigis_EcalTriggerPrimitives_L1NTUPLE.obj.obj");

    TCanvas * c2 = new TCanvas("c2", "", 1400, 900);
    c2->Divide(2,2);
    c2->cd(1);
    Events->Draw("simHcalTPs.SOI_compressedEt()", "simHcalTPs.SOI_compressedEt()>0");
    c2->cd(2);
    gPad->SetTicks(1,1);
    Events->Draw("simHcalTPs.id().iphi():simHcalTPs.id().ieta()>>h_hcaltps(64,-32,32,72,0,72)", "simHcalTPs.SOI_compressedEt()", "COLZTEXT");
    h_hcaltps->SetTitle(";simHcalTPs.id().ieta();simHcalTPs.id().iphi()");
    c2->cd(3);
    Events->Draw("ecalTPs.compressedEt()", "ecalTPs.compressedEt()>0");
    c2->cd(4);
    gPad->SetTicks(1,1);
    Events->Draw("ecalTPs.id().iphi():ecalTPs.id().ieta()", "ecalTPs.compressedEt()>0", "COLZTEXT");
    c2->SaveAs("HcalEcalTP.pdf");
}
