#include "TFile.h"
#include "TF1.h"
#include "TGraphErrors.h"
#include <iostream>
#include <TCanvas.h>

class tuneFits{

	TGraphErrors * graph;
	TF1 * newFit;
	double xmin;
	double xmax;
public:
	void setup(string,string);
	void redoFit(double,double);
	void save(string);
};

void tuneFits::setup(string inputRootFileName, string etaRange)
{
	TFile * file = TFile::Open(inputRootFileName.c_str());
// 2.65_3.139

	string graphName = "l1corr_eta_" + etaRange;
	graph = (TGraphErrors*)file->Get(graphName.c_str());

	string oldFitName = "fitfcneta_" + etaRange;
	TF1 * oldFit = (TF1*)file->Get(oldFitName.c_str());
	xmin = oldFit->GetXmin();
	xmax = oldFit->GetXmax();
	cout << endl;
	cout << "oldFit parameters: " << endl;
	cout << "p0: " << oldFit->GetParameter(0) << endl;
	cout << "p1: " << oldFit->GetParameter(1) << endl;
	cout << "p2: " << oldFit->GetParameter(2) << endl;
	cout << "p3: " << oldFit->GetParameter(3) << endl;
	cout << "p4: " << oldFit->GetParameter(4) << endl;
	cout << "p5: " << oldFit->GetParameter(5) << endl;
	cout << "p6: " << oldFit->GetParameter(6) << endl;
	cout << "oldFit xmin: " << xmin << endl;
	cout << "oldFit xmax: " << xmax << endl << endl;					

	// string newFitName = 
	newFit = new TF1(oldFitName.c_str(), "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))");
	newFit->SetParameter(0, oldFit->GetParameter(0));
	newFit->SetParameter(1, oldFit->GetParameter(1));
	newFit->SetParameter(2, oldFit->GetParameter(2));
	newFit->SetParameter(3, oldFit->GetParameter(3));
	newFit->SetParameter(4, oldFit->GetParameter(4));
	newFit->SetParameter(5, oldFit->GetParameter(5));
	newFit->SetParameter(6, oldFit->GetParameter(6));

	graph->Draw();
	oldFit->Draw("same");
	return;						
}

// note that plots will keep the same 'browser range' from earlier
void tuneFits::redoFit(double posRelToXmin, double posRelToXmax)
{
	cout << "Fitting between the ranges: " << xmin + posRelToXmin << " and " << xmax + posRelToXmax;
	graph->Fit(newFit, "", "", xmin + posRelToXmin, xmax + posRelToXmax);
	graph->Draw("AL");
}

// make a function that just draws the current status

void tuneFits::save(string outputFilename)
{ 
	// updates current file or creates it if it does not exist
	// does not overwrite, creates a second version
	TFile g(outputFilename.c_str(), "update");
	graph->Write();
	newFit->Write();
}
