// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     DeltaR_Matcher
//
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 12 Nov 2014 21:21:28 GMT
//

#include <algorithm>    // std::sort
#include <boost/bind.hpp>

#include "TGraph.h"

#include "DeltaR_Matcher.h"


/////////////////////////////////
// constructors and destructor //
/////////////////////////////////
DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR) :
maxDeltaR_(maxDeltaR),
minRefJetPt_(0.0),
minL1JetPt_(0.0),
maxJetEta_(99)
{};


DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR, const double minRefJetPt, const double minL1JetPt, const double maxJetEta) :
maxDeltaR_(maxDeltaR),
minRefJetPt_(minRefJetPt),
minL1JetPt_(minL1JetPt),
maxJetEta_(maxJetEta)
{};


DeltaR_Matcher::~DeltaR_Matcher()
{
}

//////////////////////
// member functions //
//////////////////////

void DeltaR_Matcher::setRefJets(std::vector<TLorentzVector> refJets)
{
    refJets_ = refJets;
    std::sort(refJets_.begin(), refJets_.end(), DeltaR_Matcher::sortPtDescending);
}


void DeltaR_Matcher::setL1Jets(std::vector<TLorentzVector> l1Jets)
{
    l1Jets_ = l1Jets;
    std::sort(l1Jets_.begin(), l1Jets_.end(), DeltaR_Matcher::sortPtDescending);
}


std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::getMatchingPairs()
{
    // TODO: throw exception if no vectors?
    // TODO: do I need to worry about this being deleted at end of mathod?
    std::vector<std::pair<TLorentzVector, TLorentzVector>> matchedJets; // to hold matching pairs
    for (const auto &l1_it: l1Jets_)
    {
        if (!checkJetPt(l1_it, minL1JetPt_) || !checkJetEta(l1_it, maxJetEta_))
        {
            continue;
        }

        // store matching ref jets & their deltaR for this l1 jet
        std::vector<std::pair<TLorentzVector,double>> possibleMatches;

        // for each, calculate deltaR, add to vector if satisfies maxDeltaR
        for (const auto &ref_it: refJets_)
        {
            if (!checkJetPt(ref_it, minRefJetPt_) || !checkJetEta(ref_it, maxJetEta_))
            {
                continue;
            }

            double deltaR = ref_it.DeltaR(l1_it);
            if (deltaR < maxDeltaR_)
            {
                possibleMatches.push_back(std::make_pair(ref_it, deltaR));
            }

        }

        // after matching, we want the closest ref jet (if it exists)
        if (possibleMatches.size() == 0)
        {
            continue;
        }
        else
        {
            if (possibleMatches.size() != 1)
            {
                // sort by ascending deltaR
                std::sort(possibleMatches.begin(), possibleMatches.end(),
                    boost::bind(&std::pair<TLorentzVector, double>::second, _1) <
                    boost::bind(&std::pair<TLorentzVector, double>::second, _2));
            }
            matchedJets.push_back(std::make_pair(possibleMatches[0].first, l1_it));
            // remove sucessfully matched refJet from vector of possible matches so it can't be used again
            // uses Erase-Remove idiom: https://en.wikipedia.org/wiki/Erase-remove_idiom
            refJets_.erase(remove(refJets_.begin(), refJets_.end(), possibleMatches[0].first), refJets_.end());
        }
    }
    matchedJets_ = matchedJets;
    return matchedJets;
}


bool DeltaR_Matcher::checkJetPt(const TLorentzVector& jet, const double minPt) const
{
    return (jet.Pt() >= minPt);
}


bool DeltaR_Matcher::checkJetEta(const TLorentzVector& jet, const double maxEta) const
{
    return (fabs(jet.Eta()) <= maxEta);
}


TMultiGraph* DeltaR_Matcher::plotJets()
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
    l1JetGraph->SetMarkerStyle(21);
    l1JetGraph->SetMarkerColor(kGreen+1);
    matchJetGraph->SetMarkerStyle(22);
    matchJetGraph->SetMarkerColor(kRed);

    // add graphs to TMultiGraph and return it
    TMultiGraph* plots = new TMultiGraph("plotJets",";#eta;#phi");
    plots->Add(refJetGraph, "p");
    plots->Add(l1JetGraph, "p");
    plots->Add(matchJetGraph, "p");

    return plots;
}