#include "TFile.h"
#include "TF1.h"
#include "TGraphErrors.h"
#include "TAxis.h"
#include <iostream>
#include <TCanvas.h>
#include <vector>

/*
HOW TO USE

load up this class in a ROOT session
$ .L $CMSSW_BASE/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/tuneFits.h+

$ tuneFits t0 = tuneFits("fileNameToTune.root", 0)
$ t0.redoFit(delta_xMin, delta_xMax) <--try to get a better fit, can repeat multiple times
$ t0.save()

loop through for t0, t1, t2 ... t15
e.g.
$ tuneFits t1 = tuneFits("fileNameToTune.root", 1)
etc.

NOTES:
-once you have saved a tuneFits object you cannot redoFit() or save() again, so make sure you are happy with the results before saving!
-if you try and save a tuneFits object for an eta range already used it will not work, this is to avoid overwriting previous results
-DO NOT work on the initial file, work on a copy in case you don't like the results and need to restart
*/

class tuneFits{

public:
	tuneFits(const string&, const size_t&);
	void redoFit(const double&, const double&);
	void save();

private:	
	TFile * file;
	TGraphErrors * graph;
	TF1 * newFit;
	TCanvas * c;
	double xmin_init; // initial
	double xmax_init;
	double xmin_new; // most recent used in manual fit
	double xmax_new;
	std::vector<std::string> etaBinRange;
	size_t etaBinLabel;
	bool haveSaved;
};

tuneFits::tuneFits(const std::string& inputRootFileName, const size_t& etaBin) :
file(TFile::Open(inputRootFileName.c_str(), "update")),
graph(0),
newFit(new TF1("newFit", "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))")),
c(new TCanvas("c","c")),
xmin_new(0),
xmax_new(0),
etaBinRange({"0_0.435", "0.435_0.783", "0.783_1.131", "1.131_1.305", "1.305_1.479", "1.479_1.653", "1.653_1.83", "1.83_1.93", "1.93_2.043", "2.043_2.172", "2.172_2.322", "2.322_2.5", "2.5_2.964", "2.964_3.489", "3.489_4.191", "4.191_5.191"}),
etaBinLabel(etaBin),
haveSaved(false)
{
	if (etaBinLabel > etaBinRange.size()-1){
		std::cout << "@@@ whatup FOOL @@@" << std::endl;
		std::cout << "You did not provide a valid eta bin" << std::endl;
		std::cout << "It should be a size_t between 0 and " << etaBinRange.size()-1 << std::endl;
		std::cout << "WARNING: Using the first eta bin by default" << std::endl;
		etaBinLabel = 0;
	}
	std::string graphNameGrab = "l1corr_eta_" + etaBinRange[etaBinLabel];
	graph = (TGraphErrors*)file->Get(graphNameGrab.c_str());
	std::string graphNameUse = "l1corr_eta_" + etaBinRange[etaBinLabel] + "_fit";
	graph->SetName(graphNameUse.c_str());

	std::string fitName = "fitfcneta_" + etaBinRange[etaBinLabel];
	TF1 * oldFit = (TF1*)file->Get(fitName.c_str());
	xmin_init = oldFit->GetXmin();
	xmax_init = oldFit->GetXmax();
	std::cout << std::endl;
	std::cout << "*** eta range = " + etaBinRange[etaBinLabel] << " ***" << std::endl;
	std::cout << "below are the OldFit parameters: " << std::endl;

	newFit->SetParameter(0, oldFit->GetParameter(0));
	newFit->SetParameter(1, oldFit->GetParameter(1));
	newFit->SetParameter(2, oldFit->GetParameter(2));
	newFit->SetParameter(3, oldFit->GetParameter(3));
	newFit->SetParameter(4, oldFit->GetParameter(4));
	newFit->SetParameter(5, oldFit->GetParameter(5));
	newFit->SetParameter(6, oldFit->GetParameter(6));

	redoFit(0.0, 0.0); // the TBrowser axis ranges you select for the resulting plot will be used going forward
}


void tuneFits::redoFit(const double& posRelToXmin, const double& posRelToXmax)
{
	if (haveSaved == true){
		std::cout << "This tuneFits object has already been saved! Cannot redo fit now! Not redo-ing fit..." << std::endl;
		return;
	}
	xmin_new = xmin_init + posRelToXmin;
	xmax_new = xmax_init + posRelToXmax;

	std::cout << std::endl << "Fitting between the ranges: " << xmin_new << " and " << xmax_new << std::endl << std::endl;
	graph->Fit(newFit, "", "", xmin_new, xmax_new);
	std::cout << std::endl;
	graph->Draw("AL");
	return;
}


void tuneFits::save()
{ 
	if (haveSaved == true){
		std::cout << "This tuneFits object has already been saved! Cannot save again! Not Saving..." << std::endl;
		return;
	}
	// set the ranges to match the fit range(ish)
	graph->GetXaxis()->SetRangeUser(0,xmax_new); // NB: will use the y-axis of how you were looking at it in TBrowser
	// it is not as simple for a function
	std::string fitName = "EDITFIT_fitfcneta_" + etaBinRange[etaBinLabel];
	TF1 * saveNewFit = new TF1(fitName.c_str(), "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))", xmin_new, xmax_new);
	saveNewFit->SetParameter(0, newFit->GetParameter(0));
	saveNewFit->SetParameter(1, newFit->GetParameter(1));
	saveNewFit->SetParameter(2, newFit->GetParameter(2));
	saveNewFit->SetParameter(3, newFit->GetParameter(3));
	saveNewFit->SetParameter(4, newFit->GetParameter(4));
	saveNewFit->SetParameter(5, newFit->GetParameter(5));
	saveNewFit->SetParameter(6, newFit->GetParameter(6));

	// save with same names + EDITFIT prefix
	std::string graphNameUse = "EDITFIT_l1corr_eta_" + etaBinRange[etaBinLabel] + "_fit";
	// first check save object doesn't already exist
	if ((TGraphErrors*)file->Get(graphNameUse.c_str())!=0){
		std::cout << "The graphs you are trying to save already exist! Maybe you have accidentally used the same etaBin. Don't want to overwrite, Not Saving..." << std::endl;
		c->Close();
		return;		
	}
	graph->SetName(graphNameUse.c_str());
	graph->Write();
	saveNewFit->Write();
	file->Close();
	c->Close();
	haveSaved = true;
	return;
}