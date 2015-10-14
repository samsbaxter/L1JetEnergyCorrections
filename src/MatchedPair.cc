// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     MatchedPair
// 
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Thu, 05 Feb 2015 09:30:51 GMT
//

// system include files

// user include files
#include "MatchedPair.h"


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
MatchedPair::MatchedPair(TLorentzVector refJet, TLorentzVector l1Jet):
refJet_(refJet),
l1Jet_(l1Jet)
{
}

// MatchedPair::MatchedPair(const MatchedPair& rhs)
// {
//    refJet_ = rhs.refJet();
//    l1Jet_ = rhs.l1Jet();
// }

MatchedPair::~MatchedPair()
{
}

//
// assignment operators
//
// const MatchedPair& MatchedPair::operator=(const MatchedPair& rhs)
// {
//   //An exception safe implementation is
//   MatchedPair temp(rhs);
//   swap(rhs);
//
//   return *this;
// }

//
// member functions
//
std::ostream& operator<< (std::ostream& os, const MatchedPair& pair) {
    os << "Matched pair:"
    << "\n\trefJet: pT: " << pair.refJet_.Pt()
    << ", eta: " << pair.refJet_.Eta()
    << ", phi: " << pair.refJet_.Phi()
    << "\n\tl1Jet: pT: " << pair.l1Jet_.Pt()
    << ", eta: " << pair.l1Jet_.Eta()
    << ", phi: " << pair.l1Jet_.Phi()
    << "\n\tresponse (L1/Ref): " << pair.l1Jet_.Pt()/pair.refJet_.Pt()
    << ", deltaR: " << pair.l1Jet_.DeltaR(pair.refJet_) << "\n";
    return os;
}

//
// const member functions
//

//
// static member functions
//
