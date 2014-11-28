#ifndef L1Trigger_L1JetEnergyCorrections_Matcher_h
#define L1Trigger_L1JetEnergyCorrections_Matcher_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     Matcher
//
/**\class Matcher Matcher.h "L1Trigger/L1JetEnergyCorrections/interface/Matcher.h"

 Description: Base class that defines interface for all Matcher implementations.

 Usage:
    <usage>

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 12 Nov 2014 21:17:23 GMT
//
#include <iostream>

#include "TLorentzVector.h"
#include "TGraph.h"
#include "TMultiGraph.h"

/**
 * @brief Base class that defines interface for all Matcher implementations.
 * @details A "Matcher" takes in 2 collections: one reference jet collection, and
 * one collection of L1 jets. It outputs pairs of reference & L1 jets that
 * "match" based on some criteria. Different matching schemes should be
 * implemented as classes that inherit from this class. This keeps a
 * consistent, clean interface for whatever program is using a Matcher derivation.
 */
class Matcher
{

public:

    /**
     * @brief Set reference jet collection (e.g. GenJets)
     *
     * @param refJets std::vector of TLorentzVector holding reference jets
     */
    virtual void setRefJets(std::vector<TLorentzVector> refJets) = 0;

    /**
     * @brief Set L1 jet collection (e.g. from GCT)
     *
     * @param l1Jets std::vector of TLorentzVector holding L1 jets
     */
    virtual void setL1Jets(std::vector<TLorentzVector> l1Jets) = 0;

    /**
     * @brief Produce pairs of L1 jets matched to reference jets based on some criteria.
     * @details Details of how matching is done will be provided by derived classes.
     * @return Returns a vector of std::pair of matched jets, where
     * pair.first = reference jet, pair.second = L1 jet
     */
    virtual std::vector<std::pair<TLorentzVector,TLorentzVector>> getMatchingPairs() = 0;

    /**
     * @brief Dummy function to print out basic details.
     */
    virtual void printName() const { std::cout << "I am a abstract Matcher." << std::endl; };

    /**
     * @brief Debug function to print out details of matching pairs.
     */
    virtual void printMatches() const {
        std::cout << "Matches:" << std::endl;
        if (matchedJets_.size() != 0) {
            for (auto &it: matchedJets_) { std::cout << "\nrefjet: "; it.first.Print(); std::cout << "l1jet: "; it.second.Print();}
        } else { std::cout << "<NONE>" << std::endl; };
    };

    /**
     * @brief Plots ref jets, L1 jets, and matched jet pairs on a TMultiGraph
     * @details [long description]
     * @return  TMultiGraph containing separate TGraphs for refJets (blue),
     * l1Jets (green), matchedPairs (red)
     */
    virtual TMultiGraph* plotJets()
    {
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

        TGraph * refJetGraph = new TGraph(refEta.size(), &refEta[0], &refPhi[0]);
        TGraph * l1JetGraph = new TGraph(l1Eta.size(), &l1Eta[0], &l1Phi[0]);
        TGraph * matchJetGraph = new TGraph(matchEta.size(), &matchEta[0], &matchPhi[0]);

        // styling
        refJetGraph->SetMarkerStyle(20);
        refJetGraph->SetMarkerColor(kBlue);
        refJetGraph->SetMarkerSize(1.2);
        refJetGraph->SetName("refJetGraph");
        l1JetGraph->SetMarkerStyle(21);
        l1JetGraph->SetMarkerColor(kGreen+1);
        l1JetGraph->SetMarkerSize(1.2);
        l1JetGraph->SetName("l1JetGraph");
        matchJetGraph->SetMarkerStyle(22);
        matchJetGraph->SetMarkerColor(kRed);
        matchJetGraph->SetName("matchJetGraph");

        // add graphs to TMultiGraph and return it
        TMultiGraph* plots = new TMultiGraph("plotJets",";#eta;#phi");
        plots->Add(refJetGraph, "p");
        plots->Add(l1JetGraph, "p");
        plots->Add(matchJetGraph, "p");

        return plots;
    }

protected:
    std::vector<TLorentzVector> refJets_; //!< to store reference jet collection
    std::vector<TLorentzVector> l1Jets_; //!< to store L1 jet collection
    std::vector<std::pair<TLorentzVector,TLorentzVector>> matchedJets_; //!< to store matches
};

#endif /* L1JetEnergyCorrections_Matcher_h */
