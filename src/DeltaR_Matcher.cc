// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     DeltaR_Matcher
//
// Implementation:
//     For more comments, see header file.
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 12 Nov 2014 21:21:28 GMT
//
#include "DeltaR_Matcher.h"

// STL include
#include <algorithm>    // std::sort

// BOOST include
#include <boost/bind.hpp>

// User include

using std::cout;
using std::endl;

/////////////////////////////////
// constructors and destructor //
/////////////////////////////////
DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR) :
    maxDeltaR_(maxDeltaR),
    minRefJetPt_(0.0),
    maxRefJetPt_(9999.0),
    minL1JetPt_(0.0),
    maxL1JetPt_(9999.0),
    maxJetEta_(99)
{};


DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR,
                               const double minRefJetPt,
                               const double maxRefJetPt,
                               const double minL1JetPt,
                               const double maxL1JetPt,
                               const double maxJetEta) :
    maxDeltaR_(maxDeltaR),
    minRefJetPt_(minRefJetPt),
    maxRefJetPt_(maxRefJetPt),
    minL1JetPt_(minL1JetPt),
    maxL1JetPt_(maxL1JetPt),
    maxJetEta_(maxJetEta)
{};


DeltaR_Matcher::~DeltaR_Matcher()
{
}

//////////////////////
// member functions //
//////////////////////

void DeltaR_Matcher::setRefJets(const std::vector<TLorentzVector>& refJets)
{
    refJets_.clear();
    for (const auto &jetIt: refJets)
    {
        if (checkRefJet(jetIt)) {
            refJets_.push_back(jetIt);
        }
    }
    std::sort(refJets_.begin(), refJets_.end(), DeltaR_Matcher::sortPtDescending);
}


bool DeltaR_Matcher::checkRefJet(const TLorentzVector& jet)
{
    return (checkJetMinPt(jet, minRefJetPt_)
        && checkJetMaxPt(jet, maxRefJetPt_)
        && checkJetMaxEta(jet, maxJetEta_));
}


void DeltaR_Matcher::setL1Jets(const std::vector<TLorentzVector>& l1Jets)
{
    l1Jets_.clear();
    for (const auto &jetIt: l1Jets)
    {
        if (checkL1Jet(jetIt)) {
            l1Jets_.push_back(jetIt);
        }
    }
    std::sort(l1Jets_.begin(), l1Jets_.end(), DeltaR_Matcher::sortPtDescending);
}


bool DeltaR_Matcher::checkL1Jet(const TLorentzVector& jet)
{
    return (checkJetMinPt(jet, minL1JetPt_)
        && checkJetMaxPt(jet, maxL1JetPt_)
        && checkJetMaxEta(jet, maxJetEta_));
}


std::vector<MatchedPair> DeltaR_Matcher::getMatchingPairs()
{
    matchedJets_.clear();

    // make a vector of pointers to refJets - this way we can remove successfully
    // matched refJets from possible matches so they can't be used again
    std::vector<TLorentzVector*> refJetPtrs;
    for (auto &ref_it: refJets_ )
    {
        refJetPtrs.push_back(&ref_it);
    }

    // TODO: throw exception if no vectors?
    // TODO: do I need to worry about this being deleted at end of mathod?
    std::vector<MatchedPair> matchedJets; // to hold matching pairs
    for (const auto &l1_it: l1Jets_)
    {
        // store all matching ref jets & their deltaR for this l1 jet
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
            MatchedPair m(*(possibleMatches[0].first), l1_it);
            matchedJets.push_back(m);
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


bool DeltaR_Matcher::checkJetMaxPt(const TLorentzVector& jet, const double maxPt) const
{
    return (jet.Pt() <= maxPt);
}


bool DeltaR_Matcher::checkJetMaxEta(const TLorentzVector& jet, const double maxEta) const
{
    return (fabs(jet.Eta()) <= maxEta);
}