#ifndef DELTARMATCHER_H
#define DELTARMATCHER_H

#include "Matcher.h"
#include "TLorentzVector.h"
#include <iostream>

/**
 * @brief Implementation of jet matcher using delta R between jets.
 * @details DeltaR defined as:
 * (deltaR)^2 = (deltaEta)^2 + (deltaPhi)^2
 * A L1 jet and ref jet will sucessfully match if deltaR < maxDeltaR,
 * where maxDeltaR must be passed to the object constructor.
 *
 * There is also a pT cut on reference and L1 jets. By default, these are set to 0.
 * If you want non-zero cut values, use the relevant constructor.
 */
class DeltaR_Matcher : public Matcher
{

public:

    /**
     * @brief Constructor specifying maximum DeltaR. Defaults minRefJetPt and minL1JetPt = 0.
     * @details [long description]
     *
     * @param maxDeltaR Maximum deltaR for matching between ref and L1 jet.
     */
    DeltaR_Matcher(const double maxDeltaR);

    /**
     * @brief Constructor, specifying maxDeltaR, minRefJetPt and maxjetPt.
     * @details [long description]
     *
     * @param maxDeltaR Maximum deltaR for matching between ref and L1 jet.
     * @param minRefJetPt Minimum pT a reference jet must have to participate in matching [GeV].
     * @param minL1JetPt Minimum pT a L1 jet must have to participate in matching [GeV].
     */
    DeltaR_Matcher(const double maxDeltaR, const double minRefJetPt, const double minL1JetPt);

    // @TODO: make these const refs or something. but no copying!

    /**
     * @brief Set reference jet collection (e.g. GenJets)
     * @details [long description]
     *
     * @param refJets std::vector of TLorentzVector holding reference jets
     */
    void setRefJets(std::vector<TLorentzVector> refJets);

    /**
     * @brief Set L1 jet collection (e.g. from GCT)
     * @details [long description]
     *
     * @param l1Jets std::vector of TLorentzVector holding L1 jets
     */
    void setL1Jets(std::vector<TLorentzVector> l1Jets);

    /**
     * @brief Match L1 jets to reference jets based on deltaR(refJet-l1Jet)
     * @details We loop over all combinations of reference & L1 jets. For each pair, we calculate deltaR
     * between the jets. If deltaR < _maxDeltaR, it counts as a match.
     * If there are > 1 possible matches, the one with the smallest deltaR is used.
     * @return Returns a vector of std::pair of matched jets. pair.first = reference jet, pair.second = L1 jet
     */
    std::vector<std::pair<TLorentzVector,TLorentzVector>> produceMatchingPairs();

    /**
     * @brief Check if jet pT > minPt .
     * @details [long description]
     *
     * @param jet Jet under test.
     * @param minPt Minimum pT cut value.
     *
     * @return Whether jet passed test.
     */
    bool checkJetPt(TLorentzVector jet, const double minPt);

    /**
     * @brief Dummy function to print out basic details.
     * @details [long description]
     */
    void printName() { std::cout << "I am a deltaR Matcher, with max DeltaR " << _maxDeltaR
                        << ", matching reference jets with pT > " << _minRefJetPt
                        << " and L1 jet with pT > " << _minL1JetPt << std::endl; };

private:
    std::vector<TLorentzVector> _refJets; // to store reference jet collection
    std::vector<TLorentzVector> _l1Jets; // to store L1 jet collection
    std::vector<std::pair<TLorentzVector,TLorentzVector>> _matchedJets; // to store matches
    const double _maxDeltaR; // Maximum deltaR between reference and L1 jet to count as a 'match'.
    const double _minRefJetPt; // Minimum pT for reference jet to take part in matching.
    const double _minL1JetPt; // Minimum pT for L1 jet to take part in matching.

};

#endif /* DELTARMATCHER_H */