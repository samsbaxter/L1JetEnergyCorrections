#ifndef L1Trigger_L1JetEnergyCorrections_Matcher_h
#define L1Trigger_L1JetEnergyCorrections_Matcher_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     Matcher
//
/**\class Matcher Matcher.h "L1Trigger/L1JetEnergyCorrections/interface/Matcher.h"

 Description: Base class that defines interface for all Matcher implementations.

 Usage:
    <usage>

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 12 Nov 2014 21:17:23 GMT
//

#include "TLorentzVector.h"
#include <iostream>

/**
 * @brief Base class that defines interface for all Matcher implementations.
 * @details A "Matcher" takes in 2 collections: one reference jet collection, and
 * one collection of L1 jets. It outputs pairs of reference & L1 jets that
 * "match" based on some criteria. Different matching schemes should be
 * implemented as classes that inherit from this class. This keeps a
 * consistent, clean interface for whatever program is using a Matcher derivation.
 */
class Matcher
{

public:

    /**
     * @brief Set reference jet collection (e.g. GenJets)
     *
     * @param refJets std::vector of TLorentzVector holding reference jets
     */
    virtual void setRefJets(std::vector<TLorentzVector> refJets) = 0;

    /**
     * @brief Set L1 jet collection (e.g. from GCT)
     *
     * @param l1Jets std::vector of TLorentzVector holding L1 jets
     */
    virtual void setL1Jets(std::vector<TLorentzVector> l1Jets) = 0;

    /**
     * @brief Produce pairs of L1 jets matched to reference jets based on some criteria.
     * @details Details of how matching is done will be provided by derived classes.
     * @return Returns a vector of std::pair of matched jets, where
     * pair.first = reference jet, pair.second = L1 jet
     */
    virtual std::vector<std::pair<TLorentzVector,TLorentzVector>> produceMatchingPairs() = 0;

    /**
     * @brief Dummy function to print out basic details.
     */
    virtual void printName() { std::cout << "I am a abstract Matcher." << std::endl; };

    /**
     * @brief Debug function to print out details of matching pairs.
     */
    virtual void printMatches(std::vector<std::pair<TLorentzVector,TLorentzVector>> results) {
        std::cout << "Matches:" << std::endl;
        if (results.size() != 0) {
            for (auto &it: results) { std::cout << "\nrefjet: "; it.first.Print(); std::cout << "l1jet: "; it.second.Print();}
        } else { std::cout << "<NONE>" << std::endl; };
    };
};

#endif /* L1JetEnergyCorrections_Matcher_h */
