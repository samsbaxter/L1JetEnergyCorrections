#ifndef L1Trigger_L1JetEnergyCorrections_MatchedPair_h
#define L1Trigger_L1JetEnergyCorrections_MatchedPair_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     MatchedPair
// 
/**\class MatchedPair MatchedPair.h "L1Trigger/L1JetEnergyCorrections/interface/MatchedPair.h"

 Description: Basic class to hold matched pair of reference jet and L1 jet.
 Maybe this should just be a struct? Maybe should be derived from std::pair

 Usage:
    <usage>

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Thu, 05 Feb 2015 09:30:51 GMT
//

// system include files
#include <iostream>
#include "TLorentzVector.h"

// user include files

// forward declarations

class MatchedPair
{

   public:
      MatchedPair(TLorentzVector refJet, TLorentzVector l1Jet);
      virtual ~MatchedPair();

      // ---------- const member functions ---------------------

      TLorentzVector refJet() const { return refJet_; };
      TLorentzVector l1Jet() const { return l1Jet_; };

      // ---------- static member functions --------------------

      // ---------- member functions ---------------------------

   private:
      // MatchedPair(const MatchedPair&); // stop default

      // const MatchedPair& operator=(const MatchedPair&); // stop default

      // ---------- member data --------------------------------
      TLorentzVector refJet_;
      TLorentzVector l1Jet_;
};


#endif
