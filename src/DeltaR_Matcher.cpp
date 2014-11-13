#include "DeltaR_Matcher.h"
#include <boost/bind.hpp>

DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR) :
_maxDeltaR(maxDeltaR),
_minRefJetPt(0.0),
_minL1JetPt(0.0),
_maxJetEta(5.0)
{};


DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR, double minRefJetPt, double minL1JetPt, double maxJetEta) :
_maxDeltaR(maxDeltaR),
_minRefJetPt(minRefJetPt),
_minL1JetPt(minL1JetPt),
_maxJetEta(maxJetEta)
{};


void DeltaR_Matcher::setRefJets(std::vector<TLorentzVector> refJets)
{
    _refJets = refJets;
}


void DeltaR_Matcher::setL1Jets(std::vector<TLorentzVector> l1Jets)
{
    _l1Jets = l1Jets;
}


bool DeltaR_Matcher::checkJetPt(TLorentzVector jet, const double minPt)
{
    return jet.Pt() >= minPt;
}


bool DeltaR_Matcher::checkJetEta(TLorentzVector jet, const double maxEta)
{
    return fabs(jet.Eta()) <= maxEta;
}


std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::produceMatchingPairs()
{

    // loop over reference jets
    for (const auto &ref_it: _refJets)
    {

        if (!checkJetPt(ref_it, _minRefJetPt) || !checkJetEta(ref_it, _maxJetEta))
        {
            continue;
        }

        // store matching L1 jets & their deltaR for this ref jet
        std::vector<std::pair<TLorentzVector,double>> possibleMatches;

        // loop over L1 jets
        // for each, calculate deltaR, add to above vector if satisfies maxDeltaR
        for (const auto &l1_it: _l1Jets)
        {

            if (!checkJetPt(l1_it, _minL1JetPt) || !checkJetEta(l1_it, _maxJetEta))
            {
                continue;
            }

            // @TODO: NEED TO ADD CHECK THAT WE HAVEN'T ALREADY USED THIS L1 JET

            double deltaR = ref_it.DeltaR(l1_it);
            if (deltaR < _maxDeltaR)
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
            _matchedJets.push_back(std::make_pair(ref_it, possibleMatches.at(0).first));
        }
        else
        {
            // sort by ascending deltaR
            std::sort(possibleMatches.begin(), possibleMatches.end(),
                boost::bind(&std::pair<TLorentzVector, double>::second, _1) <
                boost::bind(&std::pair<TLorentzVector, double>::second, _2));
            _matchedJets.push_back(std::make_pair(ref_it, possibleMatches.at(0).first));
        }
    }

    return _matchedJets;
}
