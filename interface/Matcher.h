#ifndef MATCHER_H
#define MATCHER_H

#include "TLorentzVector.h"
#include <iostream>

/**
 * @brief Base class that defines interface for all Matcher implementations.
 * @details Different matching schemes should be implemented as classes that inherit from this class.
 * This keeps a consistent, clean interface for whatever program is using a Matcher derivation.
 */
class Matcher
{

public:

    /**
     * @brief Set reference jet collection (e.g. GenJets)
     * @details [long description]
     *
     * @param refJets std::vector of TLorentzVector holding reference jets
     */
    virtual void setRefJets(std::vector<TLorentzVector> refJets) = 0;

    /**
     * @brief Set L1 jet collection (e.g. from GCT)
     * @details [long description]
     *
     * @param l1Jets std::vector of TLorentzVector holding L1 jets
     */
    virtual void setL1Jets(std::vector<TLorentzVector> l1Jets) = 0;

    /**
     * @brief Match L1 jets to reference jets based on deltaR(refJet-l1Jet)
     * @details We loop over all combinations of reference & L1 jets. For each pair, we calculate deltaR
     * between the jets. If deltaR < _maxDeltaR, it counts as a match.
     * If there are > 1 possible matches, the one with the smallest deltaR is used.
     * @return Returns a vector of std::pair of matched jets. pair.first = reference jet, pair.second = L1 jet
     */
    virtual std::vector<std::pair<TLorentzVector,TLorentzVector>> produceMatchingPairs() = 0;

    /**
     * @brief Dummy function to print out basic details.
     * @details [long description]
     */
    virtual void printName() { std::cout << "I am a abstract Matcher." << std::endl; };
};

#endif /* MATCHER_H */
