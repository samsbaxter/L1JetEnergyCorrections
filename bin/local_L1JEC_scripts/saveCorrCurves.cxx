#include "TFile.h"
#include "TGraphErrors.h"
#include <iostream>
#include <TCanvas.h>

// $ root -q -b -l "$CMSSW_BASE/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/saveCorrCurves.cxx+"

void loadAndSave(std::string inputFile, std::string graphName, std::string etaRange)
{
	TFile * f = TFile::Open(inputFile.c_str());
	TGraphErrors * graph = (TGraphErrors*)f->Get(graphName.c_str());
	TCanvas * c = new TCanvas("c","",650,600);
	graph->Draw();
	graph->SetTitle(etaRange.c_str());
	std::string saveName = graphName+".pdf";	
	c->SaveAs(saveName.c_str());

}

void saveCorrCurves()
{
	std::string inputFile = "output_initialNtuples_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU40to50_WITH_FITS_EDIT.root";

	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_0_0.435_fit", "eta_0_0.435");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_0.435_0.783_fit", "eta_0.435_0.783");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_0.783_1.131_fit", "eta_0.783_1.131");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.131_1.305_fit", "eta_1.131_1.305");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.305_1.479_fit", "eta_1.305_1.479");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.479_1.653_fit", "eta_1.479_1.653");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.653_1.83_fit", "eta_1.653_1.83");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.83_1.93_fit", "eta_1.83_1.93");	
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_1.93_2.043_fit", "eta_1.93_2.043");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_2.043_2.172_fit", "eta_2.043_2.172");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_2.172_2.322_fit", "eta_2.172_2.322");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_2.322_2.5_fit", "eta_2.322_2.5");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_2.5_2.964_fit", "eta_2.5_2.964");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_2.964_3.489_fit", "eta_2.964_3.489");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_3.489_4.191_fit", "eta_3.489_4.191");
	loadAndSave(inputFile.c_str(), "EDITFIT_l1corr_eta_4.191_5.191_fit", "eta_4.191_5.191");	

}