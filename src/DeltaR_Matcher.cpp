#include "DeltaR_Matcher.h"

void DeltaR_Matcher::setReferenceJets(std::vector<TLorentzVector> refJets) {
    _refJets = refJets;
}

void DeltaR_Matcher::setL1Jets(std::vector<TLorentzVector> l1Jets) {
    _l1Jets = l1Jets;
}

std::vector<std::pair<TLorentzVector,TLorentzVector>> DeltaR_Matcher::produceMatchingPairs() {
    return _matchedJets;
}
