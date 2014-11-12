#include "TLorentzVector.h"


#ifndef MATCHER_H
#define MATCHER_H

/**
 * Base class that defines interface for all Matcher implementations
 */
class Matcher {

public:
    virtual void setReferenceJets(std::vector<TLorentzVector> refJets) = 0;
    virtual void setL1Jets(std::vector<TLorentzVector> l1Jets) = 0;
    virtual std::vector<std::pair<TLorentzVector,TLorentzVector>> produceMatchingPairs() = 0;

// private:

};

#endif /* MATCHER_H */
