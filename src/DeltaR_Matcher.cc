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
#include "DeltaR_Matcher.h"


/////////////////////////////////
// constructors and destructor //
/////////////////////////////////
DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR) :
maxDeltaR_(maxDeltaR),
minRefJetPt_(0.0),
minL1JetPt_(0.0),
maxJetEta_(5.0)
{};


DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR, double minRefJetPt, double minL1JetPt, double maxJetEta) :
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
    // sort by descending pT
    // std::sort(refJets_.begin(), refJets_.end(), sortPtDescending);
}


 void DeltaR_Matcher::setL1Jets(std::vector<TLorentzVector> l1Jets)
{
    l1Jets_ = l1Jets;
    // sort by descending pT
}

// bool DeltaR_Matcher::sortPtDescending(const TLorentzVector& a, const TLorentzVector& b)
// {
//     return (a.Pt() > b.Pt());
// }


 std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::produceMatchingPairs()
{

    std::vector<std::pair<TLorentzVector, TLorentzVector>> matchedJets;

    // loop over reference jets
    // for (const auto &ref_it: refJets_)
    for (const auto &l1_it: l1Jets_)
    {

        // if (!checkJetPt(ref_it, minRefJetPt_) || !checkJetEta(ref_it, maxJetEta_))
        if (!checkJetPt(l1_it, minL1JetPt_) || !checkJetEta(l1_it, maxJetEta_))
        {
            continue;
        }

        // store matching L1 jets & their deltaR for this ref jet
        std::vector<std::pair<TLorentzVector,double>> possibleMatches;

        // loop over L1 jets
        // for each, calculate deltaR, add to above vector if satisfies maxDeltaR
        // for (const auto &l1_it: l1Jets_)
        for (const auto &ref_it: refJets_)
        {

            // if (!checkJetPt(l1_it, minL1JetPt_) || !checkJetEta(l1_it, maxJetEta_))
            if (!checkJetPt(ref_it, minRefJetPt_) || !checkJetEta(ref_it, maxJetEta_))
            {
                continue;
            }

            // @TODO: NEED TO ADD CHECK THAT WE HAVEN'T ALREADY USED THIS L1 JET
            // The actual matching criteria bit here - check deltaR
            double deltaR = ref_it.DeltaR(l1_it);
            if (deltaR < maxDeltaR_)
            {
                possibleMatches.push_back(std::make_pair(l1_it, deltaR));
            }

        }

        // after matching, we want the closest L1 jet (if it exists)
        //@TODO pop the L1 jet so we can't use it again?
        if (possibleMatches.size() == 0)
        {
            continue;
        }
        else if (possibleMatches.size() == 1)
        {
            // matchedJets_.push_back(std::make_pair(ref_it, possibleMatches.at(0).first));
            matchedJets.push_back(std::make_pair(l1_it, possibleMatches.at(0).first));
        }
        else
        {
            // sort by ascending deltaR
            std::sort(possibleMatches.begin(), possibleMatches.end(),
                boost::bind(&std::pair<TLorentzVector, double>::second, _1) <
                boost::bind(&std::pair<TLorentzVector, double>::second, _2));
            matchedJets.push_back(std::make_pair(l1_it, possibleMatches.at(0).first));
        }
    }

    return matchedJets;
}


bool DeltaR_Matcher::checkJetPt(TLorentzVector jet, const double minPt)
{
    return (jet.Pt() >= minPt);
}


bool DeltaR_Matcher::checkJetEta(TLorentzVector jet, const double maxEta)
{
    return (fabs(jet.Eta()) <= maxEta);
}