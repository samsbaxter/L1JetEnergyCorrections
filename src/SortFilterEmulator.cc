// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     SortFilterEmulator
// 
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Sun, 15 Feb 2015 12:05:44 GMT
//

// system include files

// user include files
#include "SortFilterEmulator.h"


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
SortFilterEmulator::SortFilterEmulator():
    nMax_(4)
{
}

SortFilterEmulator::SortFilterEmulator(const unsigned nMax):
    nMax_(nMax)
{
}

// SortFilterEmulator::SortFilterEmulator(const SortFilterEmulator& rhs)
// {
//    // do actual copying here;
// }

SortFilterEmulator::~SortFilterEmulator()
{
}

//
// assignment operators
//
// const SortFilterEmulator& SortFilterEmulator::operator=(const SortFilterEmulator& rhs)
// {
//   //An exception safe implementation is
//   SortFilterEmulator temp(rhs);
//   swap(rhs);
//
//   return *this;
// }

//
// member functions
//
void SortFilterEmulator::setJets(const std::vector<TLorentzVector>& jets) {
    allJets_.clear();
    cenJets_.clear();
    fwdJets_.clear();

    // Store copies of jets - don't want to modify original
    for(auto& jetItr: jets) {
        allJets_.push_back(TLorentzVector(jetItr));
    }

    // First sort by pT
    std::sort(allJets_.begin(), allJets_.end(), SortFilterEmulator::sortPtDescending);

    // Rearrange by eta region, so [central jets..., fwd jets...]
    auto fwdItr = std::stable_partition(allJets_.begin(), allJets_.end(), SortFilterEmulator::isCentral);

    // Store central and forward jets as separate collections
    cenJets_ = std::vector<TLorentzVector>(allJets_.begin(), fwdItr);
    fwdJets_ = std::vector<TLorentzVector>(fwdItr, allJets_.end());

    // Now filter jets to keep top ones
    filterJets(cenJets_);
    filterJets(fwdJets_);

    // Bit complicated for allJets_ - do fwd jets first (to not screw up fwdItr)
    // then cen jets
    if ((allJets_.end() - fwdItr) > nMax_) {
        allJets_.erase(fwdItr+nMax_, allJets_.end());
    }
    if ((fwdItr - allJets_.begin()) > nMax_) {
        allJets_.erase(allJets_.begin()+nMax_, fwdItr);
    }
}


void SortFilterEmulator::filterJets(std::vector<TLorentzVector>& jets) {
    if (jets.size() > nMax_) {
        jets.erase(jets.begin()+nMax_, jets.end());
    }
}

//
// const member functions
//

//
// static member functions
//
