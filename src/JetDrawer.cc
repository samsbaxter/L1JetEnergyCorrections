// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     JetDrawer
// 
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Sat, 29 Nov 2014 11:46:23 GMT
//

// system include files

// user include files
#include "JetDrawer.h"

#include "TCanvas.h"

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
JetDrawer::JetDrawer(std::vector<TLorentzVector> refJets,
                   std::vector<TLorentzVector> l1Jets,
                   std::vector<std::pair<TLorentzVector,TLorentzVector>> matchedJets):
    refJets_(refJets),
    l1Jets_(l1Jets),
    matchedJets_(matchedJets),
    graph_(nullptr),
    refJetGraph_(nullptr),
    l1JetGraph_(nullptr),
    matchedJetGraph_(nullptr),
    legend_(nullptr)
{
    graph_  = makeGraph();
    legend_ = makeLegend();
}

// JetDrawer::JetDrawer(const JetDrawer& rhs)
// {
//    // do actual copying here;
// }

JetDrawer::~JetDrawer()
{
}

//
// assignment operators
//
// const JetDrawer& JetDrawer::operator=(const JetDrawer& rhs)
// {
//   //An exception safe implementation is
//   JetDrawer temp(rhs);
//   swap(rhs);
//
//   return *this;
// }

//
// member functions
//

void JetDrawer::drawAndSave(TString filename) {
    TCanvas c;
    graph_->Draw("ap");
    legend_->Draw();
    c.SaveAs(filename);
}


void JetDrawer::drawAndSave(TFile* file) {
    TCanvas *c = new TCanvas();
    graph_->Draw("ap");
    legend_->Draw();
    // TODO check file OK
    file->cd();
    c->Write("", TObject::kOverwrite);
}


TMultiGraph * JetDrawer::makeGraph() {

    // load (eta,phi) points into separate graphs for refJets, l1jets, matched jets
    std::vector<double> refEta, refPhi, l1Eta, l1Phi, matchEta, matchPhi;
    for (const auto &ref_it: refJets_) {
        refEta.push_back(ref_it.Eta());
        refPhi.push_back(ref_it.Phi());
    }
    for (const auto &l1_it: l1Jets_) {
        l1Eta.push_back(l1_it.Eta());
        l1Phi.push_back(l1_it.Phi());
    }
    for (const auto &match_it: matchedJets_) {
        matchEta.push_back(match_it.first.Eta());
        matchPhi.push_back(match_it.first.Phi());
        matchEta.push_back(match_it.second.Eta());
        matchPhi.push_back(match_it.second.Phi());
    }

    refJetGraph_ = new TGraph(refEta.size(), &refEta[0], &refPhi[0]);
    styleRefJetGraph(refJetGraph_);
    l1JetGraph_ = new TGraph(l1Eta.size(), &l1Eta[0], &l1Phi[0]);
    styleL1JetGraph(l1JetGraph_);
    matchedJetGraph_ = new TGraph(matchEta.size(), &matchEta[0], &matchPhi[0]);
    styleMatchedJetGraph(matchedJetGraph_);

    // package together in TMultiGraph
    TMultiGraph* plots = new TMultiGraph("JetDrawer",";#eta;#phi");
    plots->Add(refJetGraph_, "p");
    plots->Add(l1JetGraph_, "p");
    plots->Add(matchedJetGraph_, "p");

    return plots;
}


void JetDrawer::styleRefJetGraph(TGraph * graph) {
    graph->SetMarkerStyle(20);
    graph->SetMarkerColor(kBlue);
    graph->SetMarkerSize(1.2);
    graph->SetName("refJetGraph");
}


void JetDrawer::styleL1JetGraph(TGraph * graph) {
    graph->SetMarkerStyle(21);
    graph->SetMarkerColor(kGreen+1);
    graph->SetMarkerSize(1.2);
    graph->SetName("l1JetGraph");
}


void JetDrawer::styleMatchedJetGraph(TGraph * graph) {
    graph->SetMarkerStyle(22);
    graph->SetMarkerColor(kRed);
    graph->SetName("matchJetGraph");
}


TLegend * JetDrawer::makeLegend() {
    TLegend * leg = new TLegend(0.1,0.91, 0.9, 0.98);
    leg->SetNColumns(3);
    leg->AddEntry(refJetGraph_, "Reference jets", "p");
    leg->AddEntry(l1JetGraph_, "L1 jets", "p");
    leg->AddEntry(matchedJetGraph_, "Matched jets", "p");
    leg->SetFillColor(kWhite);
    leg->SetLineColor(kWhite);
    return leg;
}

//
// const member functions
//

//
// static member functions
//
