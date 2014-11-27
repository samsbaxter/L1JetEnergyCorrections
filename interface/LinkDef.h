#ifdef __MAKECINT__
// #pragma link C++ class std::vector<TLorentzVector>+;
#pragma link C++ class std::pair<TLorentzVector,TLorentzVector>+;
#pragma link C++ class std::vector<std::pair<TLorentzVector, TLorentzVector> >+;
#pragma link C++ class L1Analysis::L1AnalysisL1ExtraDataFormat+;
#endif

/**
 * This file is necessary to build dictionaries that can be used to insert objects
 * into TTrees via TBranches. To do so:
 * Run this in /interface with
 * rootcint -f dictionary.cpp -c TLorentzVector.h ../../../L1TriggerDPG/L1Ntuples/interface/L1AnalysisL1ExtraDataFormat.h LinkDef.h && mv dictionary.cpp ../src/
 * Then run scram as normal, and hopefully all should work.
 *
 * Note that, to get the vector<pair<T,T>> to work, you need the previous line
 * of pair<T,T>.
 *
 * Yes, this is bloody ridiculous. It took me half a day to figure out, with
 * much swearing.
 */
