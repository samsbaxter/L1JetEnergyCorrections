#include "TFile.h"
#include "TF1.h"
#include <iostream>
#include "TLegend.h"
#include "TStyle.h"
#include "TAxis.h"
#include <TCanvas.h>

// $ root -q -b -l "/users/jt15104/CMSSW_8_0_7/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/compareFitsQuicky.cxx+"

void makePlots(std::string,std::string,std::string);

void compareFitsQuicky(){

	std::string directory = "/users/jt15104/local_L1JEC_store/26May2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_jbntuples_dr0p25_etaBinningVersion2/runCalib_jetMetFitErr/";
	
	std::string inputFile1 = "testPU0to10.root";
	std::string outputName1 = "fitsPU0to10.pdf";

	std::string inputFile2 = "testPU15to25.root";
	std::string outputName2 = "fitsPU15to25.pdf";

	std::string inputFile3 = "testPU30to40.root";
	std::string outputName3 = "fitsPU30to40.pdf";

	makePlots(inputFile1, outputName1, directory);
	makePlots(inputFile2, outputName2, directory);
	makePlots(inputFile3, outputName3, directory);

}


void makePlots(std::string inputFile, std::string outputFile, std::string directory){

	std::string inputPath = directory + inputFile;
	std::string outputPath = directory + outputFile;

	TFile * f = TFile::Open(inputPath.c_str());

	TF1 * g00 = (TF1*)f->Get("fitfcneta_0_0.175");
	TF1 * g01 = (TF1*)f->Get("fitfcneta_0.175_0.35");
	TF1 * g02 = (TF1*)f->Get("fitfcneta_0.35_0.525");
	TF1 * g03 = (TF1*)f->Get("fitfcneta_0.525_0.7");
	TF1 * g04 = (TF1*)f->Get("fitfcneta_0.7_0.875");
	TF1 * g05 = (TF1*)f->Get("fitfcneta_0.875_1.05");
	TF1 * g06 = (TF1*)f->Get("fitfcneta_1.05_1.225");
	TF1 * g07 = (TF1*)f->Get("fitfcneta_1.225_1.4");
	TF1 * g08 = (TF1*)f->Get("fitfcneta_1.4_1.575");
	TF1 * g09 = (TF1*)f->Get("fitfcneta_1.575_1.75");
	TF1 * g10 = (TF1*)f->Get("fitfcneta_1.75_1.925");
	TF1 * g11 = (TF1*)f->Get("fitfcneta_1.925_2.1");
	TF1 * g12 = (TF1*)f->Get("fitfcneta_2.1_2.5");
	TF1 * g13 = (TF1*)f->Get("fitfcneta_2.5_3");
	TF1 * g14 = (TF1*)f->Get("fitfcneta_3_3.5");
	TF1 * g15 = (TF1*)f->Get("fitfcneta_3.5_3.9");
	TF1 * g16 = (TF1*)f->Get("fitfcneta_3.9_4.1");
	TF1 * g17 = (TF1*)f->Get("fitfcneta_4.1_4.5");
	// TF1 * g18 = (TF1*)f->Get("fitfcneta_4.5_5");

	g00->SetLineColor(kBlack);
	g01->SetLineColor(kBlue+2);
	g02->SetLineColor(kBlue);
	g03->SetLineColor(kCyan+1);
	g04->SetLineColor(kGreen+2);
	g05->SetLineColor(kGreen);	
	g06->SetLineColor(kYellow+2);
	g07->SetLineColor(kOrange);
	g08->SetLineColor(kOrange+7);
	g09->SetLineColor(kRed+2);	
	g10->SetLineColor(kRed);
	g11->SetLineColor(kMagenta+3);
	g12->SetLineColor(kMagenta);
	g13->SetLineColor(kBlack);
	g14->SetLineColor(kBlue+2);
	g15->SetLineColor(kBlue);
	g16->SetLineColor(kCyan+1);
	g17->SetLineColor(kGreen+2);
	// g18->SetLineColor(kGreen);

	TCanvas * c3 = new TCanvas("c3", "", 600, 600);
	gStyle->SetOptStat(0);
	g00->GetYaxis()->SetRangeUser(0.9,2.0);
	g00->GetXaxis()->SetRangeUser(20,300);
	g00->Draw();
	g01->Draw("same");
	g02->Draw("same");
	g03->Draw("same");
	g04->Draw("same");
	g05->Draw("same");
	g06->Draw("same");
	g07->Draw("same");
	g08->Draw("same");
	g09->Draw("same");
	g10->Draw("same");
	g11->Draw("same");
	g12->Draw("same");
	g13->Draw("same");
	g14->Draw("same");
	g15->Draw("same");
	g16->Draw("same");
	g17->Draw("same");
	// g18->Draw("same");
	
	TLegend * leg3 = new TLegend(0.43,0.53,0.88,0.88);
	leg3->AddEntry(g00, "(HB) 1,2");		
	leg3->AddEntry(g01, "3,4");
	leg3->AddEntry(g02, "5,6");
	leg3->AddEntry(g03, "7,8");
	leg3->AddEntry(g04, "9,10");
	leg3->AddEntry(g05, "11,12");
	leg3->AddEntry(g06, "13,14");
	leg3->AddEntry(g07, "15,16");
	leg3->AddEntry(g08, "(HE) 17,18");
	leg3->AddEntry(g09, "19,20");
	leg3->AddEntry(g10, "21,22");
	leg3->AddEntry(g11, "23,24");
	leg3->AddEntry(g12, "25,26");
	leg3->AddEntry(g13, "27,28");
	leg3->AddEntry(g14, "(HF) 29,30");
	leg3->AddEntry(g15, "31,32");
	leg3->AddEntry(g16, "33,34");
	leg3->AddEntry(g17, "35,36");
	// leg3->AddEntry(g18, "37,38");
	leg3->Draw();		

	c3->SaveAs(outputPath.c_str());
	c3->Close();	
}