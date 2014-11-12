#ifndef DELTARMATCHER_H
#define DELTARMATCHER_H

#include "Matcher.h"
#include "TLorentzVector.h"
#include <iostream>

/**
 * @brief Implementation of jet matching using delta R between jets
 * @details (deltaR)^2 = (deltaEta)^2 + (deltaPhi)^2
 *
 */
class DeltaR_Matcher {
public:
    DeltaR_Matcher(const double deltaR) : _deltaR(deltaR) {};
    void setReferenceJets(std::vector<TLorentzVector> refJets); // virtual?
    void setL1Jets(std::vector<TLorentzVector> l1Jets);
    std::vector<std::pair<TLorentzVector,TLorentzVector>> produceMatchingPairs();
    void printDeltaR() { std::cout << _deltaR << std::endl; };

private:
    std::vector<TLorentzVector> _refJets;
    std::vector<TLorentzVector> _l1Jets;
    std::vector<std::pair<TLorentzVector,TLorentzVector>> _matchedJets;
    const double _deltaR;
};

#endif /* DELTARMATCHER_H */