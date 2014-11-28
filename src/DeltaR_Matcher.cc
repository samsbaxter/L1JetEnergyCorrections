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

// STL include
#include <algorithm>    // std::sort

// BOOST include
#include <boost/bind.hpp>

// User include
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
    refJets_.clear();
    for (const auto &jetIt: refJets){
        if (checkRefJet(jetIt)) refJets_.push_back(jetIt);
    }
    std::sort(refJets_.begin(), refJets_.end(), DeltaR_Matcher::sortPtDescending);
}


bool DeltaR_Matcher::checkRefJet(const TLorentzVector& jet)
{
    return (jet.Pt() > minRefJetPt_) && (abs(jet.Eta()) < maxJetEta_);
}


void DeltaR_Matcher::setL1Jets(std::vector<TLorentzVector> l1Jets)
{
    l1Jets_.clear();
    for (const auto &jetIt: l1Jets){
        if (checkL1Jet(jetIt)) l1Jets_.push_back(jetIt);
    }
    std::sort(l1Jets_.begin(), l1Jets_.end(), DeltaR_Matcher::sortPtDescending);
}


bool DeltaR_Matcher::checkL1Jet(const TLorentzVector& jet)
{
    return (jet.Pt() > minL1JetPt_) && (abs(jet.Eta()) < maxJetEta_);
}


std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::getMatchingPairs()
{
    matchedJets_.clear();

    // make a vector of pointers to refJets - this way we can remove
    // successfully matched refJets from possible matches so it can't be used again
    std::vector<TLorentzVector*> refJetPtrs;
    for (auto &ref_it: refJets_ )
    {
        refJetPtrs.push_back(&ref_it);
    }

    // TODO: throw exception if no vectors?
    // TODO: do I need to worry about this being deleted at end of mathod?
    std::vector<std::pair<TLorentzVector, TLorentzVector>> matchedJets; // to hold matching pairs
    for (const auto &l1_it: l1Jets_)
    {

        // store matching ref jets & their deltaR for this l1 jet
        std::vector<std::pair<TLorentzVector*,double>> possibleMatches;

        // for each, calculate deltaR, add to vector if satisfies maxDeltaR
        for (const auto &ref_it: refJetPtrs)
        {
            double deltaR = ref_it->DeltaR(l1_it);
            if (deltaR < maxDeltaR_)
            {
                possibleMatches.push_back(std::make_pair(ref_it, deltaR));
            }
        }

        // after matching, we want the closest ref jet (if it exists)
        if (possibleMatches.size() != 0)
        {
            if (possibleMatches.size() != 1)
            {
                // sort by ascending deltaR
                std::sort(possibleMatches.begin(), possibleMatches.end(),
                    boost::bind(&std::pair<TLorentzVector*, double>::second, _1) <
                    boost::bind(&std::pair<TLorentzVector*, double>::second, _2));
            }
            matchedJets.push_back(std::make_pair(*(possibleMatches[0].first), l1_it));
            // remove sucessfully matched refJet from vector of possible matches so it can't be used again
            // uses Erase-Remove idiom: https://en.wikipedia.org/wiki/Erase-remove_idiom
            refJetPtrs.erase(remove(refJetPtrs.begin(), refJetPtrs.end(), possibleMatches[0].first), refJetPtrs.end());
        }
    }
    matchedJets_ = matchedJets;
    return matchedJets;
}


bool DeltaR_Matcher::checkJetMinPt(const TLorentzVector& jet, const double minPt) const
{
    return (jet.Pt() >= minPt);
}


bool DeltaR_Matcher::checkJetMaxEta(const TLorentzVector& jet, const double maxEta) const
{
    return (fabs(jet.Eta()) <= maxEta);
}