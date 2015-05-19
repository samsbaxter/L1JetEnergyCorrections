{
    TFile f1("L1Tree_rerunRCT_origLut.root");
    TFile f2("L1Tree_rerunRCT_newRCTLut.root");

    TTree * internTree1 = (TTree*) f1.Get("l1ExtraTreeProducerGctIntern/L1ExtraTree");
    TTree * internTree2 = (TTree*) f2.Get("l1ExtraTreeProducerGctIntern/L1ExtraTree");

    internTree1->Draw("cenJetEt>>h_et1(200,0,200)");
    internTree2->Draw("cenJetEt>>h_et2(200,0,200)");

    h_et2->SetLineColor(kRed);
    h_et1->Draw("");
    h_et2->Draw("SAME");
    c1.SaveAs("comparingJetsIntern.pdf");
}
