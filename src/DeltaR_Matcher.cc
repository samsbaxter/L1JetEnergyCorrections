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


std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::produceMatchingPairs()
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

        // store matching L1 jets & their deltaR for this ref jet
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

        // after matching, we want the closest L1 jet (if it exists)
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