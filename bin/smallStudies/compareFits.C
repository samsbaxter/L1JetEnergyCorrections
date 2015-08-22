{
    /**
     * @brief This script compares calibration fit functions and graphs form 2 different files.
     */
    TFile * f1 = TFile::Open("/hdfs/user/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/QCDSpring15_Stage1_AVE20BX25_newRCTv2/output_QCD_Pt-30to1000_Spring15_AVE20BX25_Stage1_QCDSpring15_newRCTv2_preGt_ak4_ref14to1000_l10to500_better2.root");
    TFile * f2 = TFile::Open("/users/ra12451/L1JEC/CMSSW_7_4_2/src/L1Trigger/L1JetEnergyCorrections/Stage1_QCDSpring15_AVE20BX25_stage1NoLut_rctv4_jetSeed5/output_QCD_Pt-15to170_300to1000_Spring15_AVE20BX25_Stage1_jetSeed5_MCRUN2_V9_noStage1Lut_rctv4_preGt_ak4_ref14to1000_l10to500_fitMin20_HFfix.root");

    TLegend * leg = new TLegend(0.67, 0.67, 0.88, 0.88);
    TString leg1Label("jet seed 10");
    TString leg2Label("jet seed 5");

    TCanvas * c1 = new TCanvas("c1", "", 800, 600);
    c1->SetTicks(1,1);

    std::vector<double> etaBins;
    etaBins.push_back(0.0);
    etaBins.push_back(0.348);
    etaBins.push_back(0.695);
    etaBins.push_back(1.044);
    etaBins.push_back(1.392);
    etaBins.push_back(1.74);
    etaBins.push_back(2.172);
    etaBins.push_back(3.0);
    etaBins.push_back(3.5);
    etaBins.push_back(4.0);
    etaBins.push_back(4.5);
    etaBins.push_back(5);

    double minET = 0;
    double maxET = 250;
    double minETZoom = 0;
    double maxETZoom = 50;

    double yMax = 3;
    double yMin = 0.6;

    for (int i = 0; i < etaBins.size()-1; ++i) {
        TString grName = TString::Format("fitfcneta_%g_%g", etaBins[i], etaBins[i+1]);
        cout << grName << endl;
        TF1 * form1 = (TF1*) f1->Get(grName);
        TF1 * form2 = (TF1*) f2->Get(grName);
        form1->SetTitle(TString::Format("#eta: %g - %g", etaBins[i], etaBins[i+1])+";p_{T};Correction value");
        form2->SetTitle(TString::Format("#eta: %g - %g", etaBins[i], etaBins[i+1])+";p_{T};Correction value");
        form1->SetLineColor(kRed);
        form2->SetLineColor(kBlue);

        TLine line(5,0.8, 5, 12);
        line.SetLineStyle(2);

        // auto determine y range maximum
        yMax = 1.1 * max(form1->Eval(5), form2->Eval(5));

        // compare fit functions
        form1->SetRange(minET, maxET);
        form2->SetRange(minET, maxET);
        if (form2->GetMaximum(minET, maxET) > form1->GetMaximum(minET, maxET)) {
            form2->Draw();
            form1->Draw("SAME");
        } else {
            form1->Draw();
            form2->Draw("SAME");
        }

        if (i == 0){
            leg->AddEntry(form1, leg1Label, "L");
            leg->AddEntry(form2, leg2Label, "L");
        }
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_fn.pdf");

        // redo plot but over small pT range
        form1->SetRange(minETZoom, maxETZoom);
        form2->SetRange(minETZoom, maxETZoom);
        if (form2->GetMaximum(minET, maxET) > form1->GetMaximum(minET, maxET)) {
            form2->Draw();
            form1->Draw("SAME");
        } else {
            form1->Draw();
            form2->Draw("SAME");
        }
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_fn_zoom.pdf");

        // plots the graphs by themselves
        grName = TString::Format("l1corr_eta_%g_%g", etaBins[i], etaBins[i+1]);
        cout << grName << endl;
        TGraphErrors * gr1 = (TGraphErrors*) f1->Get(grName);
        TGraphErrors * gr2 = (TGraphErrors*) f2->Get(grName);
        gr1->SetTitle(TString::Format("#eta: %g - %g", etaBins[i], etaBins[i+1]));
        gr2->SetTitle(TString::Format("#eta: %g - %g", etaBins[i], etaBins[i+1]));
        gr1->SetLineColor(kRed);
        gr2->SetLineColor(kBlue);
        gr1->GetXaxis()->SetLimits(minET, maxET);
        gr2->GetXaxis()->SetLimits(minET, maxET);
        gr1->GetYaxis()->SetRangeUser(yMin, yMax);
        gr2->GetYaxis()->SetRangeUser(yMin, yMax);
        gr2->Draw("ALP");
        gr1->Draw("SAME");
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_graph.pdf");

        // redo plot but over small pT range
        gr1->GetXaxis()->SetLimits(minETZoom, maxETZoom);
        gr2->GetXaxis()->SetLimits(minETZoom, maxETZoom);
        gr2->Draw("ALP");
        gr1->Draw("SAME");
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_graph_zoom.pdf");

        // plot graphs and functions together
        gr1->GetXaxis()->SetLimits(minET, maxET);
        gr2->GetXaxis()->SetLimits(minET, maxET);
        form1->SetRange(minET, maxET);
        form2->SetRange(minET, maxET);
        gr2->Draw("ALP");
        gr1->Draw("SAME");
        form2->Draw("SAME");
        form1->Draw("SAME");
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_both.pdf");

        // redo plot but over small pT range
        gr1->GetXaxis()->SetLimits(minETZoom, maxETZoom);
        gr2->GetXaxis()->SetLimits(minETZoom, maxETZoom);
        form1->SetRange(minETZoom, maxETZoom);
        form2->SetRange(minETZoom, maxETZoom);
        gr2->Draw("ALP");
        gr1->Draw("SAME");
        form2->Draw("SAME");
        form1->Draw("SAME");
        leg->Draw();
        c1->Update();
        line.SetY1(gPad->GetUymin());
        line.SetY2(gPad->GetUymax());
        line.Draw();
        c1->SaveAs(grName+"_compare_both_zoom.pdf");
    }

    f1->Close();
    f2->Close();
}