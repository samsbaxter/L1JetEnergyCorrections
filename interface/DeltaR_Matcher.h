#ifndef L1Trigger_L1JetEnergyCorrections_DeltaR_Matcher_h
#define L1Trigger_L1JetEnergyCorrections_DeltaR_Matcher_h

// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     DeltaR_Matcher
//
/**\class DeltaR_Matcher DeltaR_Matcher.h "L1Trigger/L1JetEnergyCorrections/interface/DeltaR_Matcher.h"

 Description: Implementation of jet matcher using delta R between jets.

 Usage:
    <usage>

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 12 Nov 2014 21:21:21 GMT
//

#include <iostream>
#include <algorithm>
#include <vector>

#include "TMultiGraph.h"

#include "Matcher.h"

#include "TLorentzVector.h"

/**
 * @brief Implementation of jet matcher using delta R between jets.
 * @details DeltaR defined as:
 * (deltaR)^2 = (deltaEta)^2 + (deltaPhi)^2. A L1 jet and ref jet will
 * sucessfully match if deltaR < maxDeltaR, where maxDeltaR must be
 * passed to the object constructor.
 *
 * There is also a pT cut on reference and L1 jets. In addition,
 * there is a maximum abs(eta) cuts on jets as well. Defaults for these are found
 * in the constructor. If you want a different cut value, use the relevant constructor or setter.
 */
class DeltaR_Matcher : public Matcher
{

public:

    /**
     * @brief Constructor specifying maximum DeltaR for matching. Set defaults for minRefJetPt, minL1JetPt, maxJetEta such that they have no effect.
     *
     * @param maxDeltaR Maximum deltaR for matching between ref and L1 jet.
     */
    DeltaR_Matcher(const double maxDeltaR);

    /**
     * @brief Constructor, specifying maximum DeltaR for matching, minRefJetPt, minL1JetPt, maxJetEta.
     *
     * @param maxDeltaR Maximum deltaR for matching between ref and L1 jet.
     * @param minRefJetPt Minimum pT a reference jet must have to participate in matching [GeV].
     * @param minL1JetPt Minimum pT a L1 jet must have to participate in matching [GeV].
     * @param maxJetEta Maximum absolute eta of any jet to participate in matching.
     */
    DeltaR_Matcher(const double maxDeltaR, const double minRefJetPt, const double minL1JetPt, const double maxJetEta);

    virtual ~DeltaR_Matcher();

    // @TODO: make these const refs or something. but no copying!

    /**
     * @brief Set reference jet collection (e.g. GenJets) & sorts by descending pT
     *
     * @param refJets std::vector of TLorentzVector holding reference jets
     */
    virtual void setRefJets(std::vector<TLorentzVector> refJets) override;

    /**
     * @brief Set L1 jet collection (e.g. from GCT) & sorts by descending pT
     *
     * @param l1Jets std::vector of TLorentzVector holding L1 jets
     */
    virtual void setL1Jets(std::vector<TLorentzVector> l1Jets) override;

    // TODO: make these protected/private as not conforming to interface?

    /**
     * @brief Set minimum jet pT cut to be applied to reference jets.
     *
     * @param jetPt Minimum pT value.
     */
    void setMinRefJetPt(double jetPt) { minRefJetPt_ = jetPt; };

    /**
     * @brief Set minimum jet pT cut to be applied to L1 jets.
     *
     * @param jetPt Minimum pT value.
     */
    void setMinL1JetPt(double jetPt) { minL1JetPt_ = jetPt; };

    /**
     * @brief Set maximum absolute jet eta cut to be applied to both L1 and ref jets.
     *
     * @param jetEta Maximum absolute Eta value
     */
    void setMaxJetEta(double jetEta) { maxJetEta_ = jetEta; };

    /**
     * @brief Produce pairs of L1 jets matched to reference jets based on deltaR(refJet-l1Jet).
     *
     * @details For each L1 jet, we loop over all reference jets. For each
     * pair, we calculate deltaR between the jets. If deltaR < maxDeltaR_, it
     * counts as a match. If there are > 1 possible matches, the one with the
     * smallest deltaR is used. Also applies min pT cut and max abs(eta) cut on
     * jets. Values of these cuts are set by associated setters or constructor.
     * Note that because the jets are sorted by pT, higher pT L1 jets get priority
     * in matching, since we remove a refJet from potential matches once matched
     * to a L1 jet.
     *
     * @return Returns a vector of std::pair of matched jets.
     * pair.first = reference jet, pair.second = L1 jet
     */
    virtual std::vector<std::pair<TLorentzVector,TLorentzVector>> getMatchingPairs() override;

    /**
     * @brief Dummy function to print out basic details.
     */
    void printName() const override { std::cout << "\nI am a deltaR Matcher, with max DeltaR " << maxDeltaR_
                        << ", matching reference jets with pT > " << minRefJetPt_
                        << " and L1 jet with pT > " << minL1JetPt_
                        << " and jet |eta| < " << maxJetEta_ << std::endl; };

    /**
     * @brief PLots ref jets, L1 jets, and matched jet pairs on a TMultiGraph
     * @details [long description]
     * @return [description]
     */
    TMultiGraph* plotJets();

private:

    /**
     * @brief Check if jet pT > minPt.
     *
     * @param jet Jet under test.
     * @param minPt Minimum pT cut value.
     *
     * @return Whether jet passed test.
     */
    bool checkJetPt(const TLorentzVector& jet, const double minPt) const;

    /**
     * @brief Check if abs(eta) of jet < maxEta.
     *
     * @param jet Jet under test.
     * @param eta Maximum absolute eta allowed.
     *
     * @return Whether jet passed test.
     */
    bool checkJetEta(const TLorentzVector& jet, const double maxEta) const;

    /**
     * @brief Binary predicate to use in std::sort, to allow sorting TLorentzVectors by descending pT
     * @details Since this is a CLASS method, need to make it static for it to work in std::sort. Maybe
     * I should make it a common function outside of the class?
     *
     * @param a One TLorentzVector
     * @param b Other TLorentzVector
     *
     * @return True if a.Pt() > b.Pt()
     */
    static bool sortPtDescending(const TLorentzVector &a, const TLorentzVector &b) { return (a.Pt() > b.Pt()); } ;

    std::vector<TLorentzVector> refJets_; // to store reference jet collection
    std::vector<TLorentzVector> l1Jets_; // to store L1 jet collection
    std::vector<std::pair<TLorentzVector,TLorentzVector>> matchedJets_; // to store matches

    const double maxDeltaR_; // Maximum deltaR between reference and L1 jet to count as a 'match'.
    double minRefJetPt_; // Minimum pT for reference jet to take part in matching.
    double minL1JetPt_; // Minimum pT for L1 jet to take part in matching.
    double maxJetEta_;  // Maximum absolute eta for any jet to take part in matching.
};

#endif /* L1Trigger_L1JetEnergyCorrections_DeltaR_Matcher_h */