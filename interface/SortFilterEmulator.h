#ifndef L1Trigger_L1JetEnergyCorrections_SortFilterEmulator_h
#define L1Trigger_L1JetEnergyCorrections_SortFilterEmulator_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     SortFilterEmulator
// 
/**\class SortFilterEmulator SortFilterEmulator.h "SortFilterEmulator.h"

 Description: Does sorting & filtering of jets (for cen & fwd separately)
                  - emulates what happens before jets passed to GT


 Usage:
     SortFilterEmulator emu(4);  // keep top 4
     emu.setJets(myJets); // loads jets & does sorting, filtering
     emu.getAllJets();
     // if you only want central jets:
     emu.getCenJets();
     // if you only want forward jets:
     emu.getFwdJets();

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Sun, 15 Feb 2015 12:05:44 GMT
//

// system include files
#include <iostream>
#include <vector>
#include <utility>
#include <stdexcept>
#include <algorithm>

// user include files
#include "TLorentzVector.h"

// forward declarations

class SortFilterEmulator
{

public:
    /**
     * @brief Default constructor of SortFilterEmulator object.
     * @details Doesn't do anything, awaiting user to call setJets().
     * By defualt, keeps 4 jets in each cen/fwd collection
     */
    SortFilterEmulator();

    /**
     * @brief Constructor allowing user to set how many jets to keep.
     *
     * @param nMax Number of jets to keep in each cen/fwd collection
     */
    SortFilterEmulator(unsigned nMax);

    virtual ~SortFilterEmulator();

    // ---------- const member functions ---------------------

    // ---------- static member functions --------------------

    // ---------- member functions ---------------------------

    /**
     * @brief [brief description]
     * @details [long description]
     *
     * @param jets [description]
     */
    void setJets(const std::vector<TLorentzVector>& jets);

    /**
     * @brief [brief description]
     * @details [long description]
     * @return [description]
     */
    std::vector<TLorentzVector> getAllJets() { return allJets_; };

    /**
     * @brief [brief description]
     * @details [long description]
     * @return [description]
     */
    std::vector<TLorentzVector> getCenJets() { return cenJets_; };

    /** // loads jets & does sorting, filtering
     * @brief [brief description]
     * @details [long description]
     * @return [description]
     */
    std::vector<TLorentzVector> getFwdJets() { return fwdJets_; };

private:
    SortFilterEmulator(const SortFilterEmulator&); // stop default

    const SortFilterEmulator& operator=(const SortFilterEmulator&); // stop default

    /**
     * @brief Binary predicate to use in std algorithms, to allow sorting TLorentzVectors by eta region
     * @details Central = |eta| < 3.0. Fwd = |eta| > 3.0.
     * Since this is a CLASS method, need to make it static for it to work in std::sort. Maybe
     * I should make it a common function outside of the class?
     *
     * @param vec TLorentzVector under test
     *
     * @return True if vec in central region, false otherwise
     */
    static bool isCentral(const TLorentzVector& vec) { return fabs(vec.Eta()) < 3.0; };

    /**
     * @brief Binary predicate to use in std algorithms, to allow sorting TLorentzVectors by descending pT
     * @details Since this is a CLASS method, need to make it static for it to work in std::sort. Maybe
     * I should make it a common function outside of the class?
     *
     * @param a One TLorentzVector
     * @param b Other TLorentzVector
     *
     * @return True if a.Pt() > b.Pt()
     */
    static bool sortPtDescending(const TLorentzVector &a, const TLorentzVector &b) { return (a.Pt() > b.Pt()); } ;

    /**
     * @brief Only keep top nMax jets in a collection
     *
     * @param jets Input collection to filter
     */
    void filterJets(std::vector<TLorentzVector>& jets);

    // ---------- member data --------------------------------
    const unsigned nMax_; // maximum number of jets to keep when filtering
    std::vector<TLorentzVector> allJets_;
    std::vector<TLorentzVector> cenJets_;
    std::vector<TLorentzVector> fwdJets_;
};


#endif
