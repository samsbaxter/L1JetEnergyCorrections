#include "DeltaR_Matcher.h"

DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR) :
_maxDeltaR(maxDeltaR),
_minRefJetPt(0.0),
_minL1JetPt(0.0)
{};


DeltaR_Matcher::DeltaR_Matcher(const double maxDeltaR, const double minRefJetPt, const double minL1JetPt) :
_maxDeltaR(maxDeltaR),
_minRefJetPt(minRefJetPt),
_minL1JetPt(minL1JetPt)
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
    return jet.Pt() > minPt;
}


std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::produceMatchingPairs()
{

    // loop over reference jets
    for (const auto &ref_it: _refJets)
    {

        if (!checkJetPt(ref_it, _minRefJetPt))
        {
            continue;
        }

        // store matching L1 jets for this ref jet
        std::vector<TLorentzVector> matches;

        // loop over L1 jets
        // for each, calculate deltaR, add to vector if satisfies maxDeltaR
        for (const auto &l1_it: _l1Jets)
        {

            if (!checkJetPt(l1_it, _minL1JetPt))
            {
                continue;
            }

            // TODO: NEED TO ADD CHECK THAT WE HAVEN'T ALREADY USED THIS L1 JET

            double deltaR = ref_it.DeltaR(l1_it);
            if (deltaR < _maxDeltaR)
            {
                matches.push_back(l1_it);
            }

        }

        // after matching, we want the closest L1 jet (if it exists)
        if (matches.size() == 0)
        {
            continue;
        }
        else if (matches.size() == 1)
        {
            // pop the L1 jet so we can't use it again?
            _matchedJets.push_back(std::make_pair(ref_it, matches.at(0)));
        }
        else
        {
            // pop the L1 jet so we can't use it again?
            // std::sort(matches.begin(), matches.end(), sortDR);
            _matchedJets.push_back(std::make_pair(ref_it, matches.at(0)));
        }
    }

    return _matchedJets;
}
