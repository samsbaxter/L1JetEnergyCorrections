#ifndef L1Trigger_L1JetEnergyCorrections_runMatcherUtils_h
#define L1Trigger_L1JetEnergyCorrections_runMatcherUtils_h

// STL headers
#include <vector>

// ROOT headers
#include "TLorentzVector.h"
#include "TF1.h"
#include "TString.h"

// L1T headers
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoJetDataFormat.h"

using L1Analysis::L1AnalysisRecoJetDataFormat;


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @return [description]
 */
template<typename T>
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<T> & et,
                                                std::vector<T> & eta,
                                                std::vector<T> & phi);


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 * Also includes requirement that BX = 0.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @param bx [description]
 * @return [description]
 */
template<typename T, typename T2>
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<T> & et,
                                                std::vector<T> & eta,
                                                std::vector<T> & phi,
                                                std::vector<T2> & bx);


/**
 * @brief Get correction functions from file, and load into vector.
 * @details Note that correction functions have names
 * "fitfcneta_<etaMin>_<etaMax>", where etaMin/Max denote eta bin limits.
 *
 * @param filename  Name of file with correction functions.
 * @param corrFns   Vector of TF1s in which functions are stored.
 */
void loadCorrectionFunctions(const TString& filename,
                             std::vector<TF1>& corrFns,
                             const std::vector<float>& etaBins);


/**
 * @brief Apply correction function to collection of jets
 * @details [long description]
 *
 * @param corrFn   Vector of TF1 to be applied, corresponding to eta bins
 * @param etaBins  Eta bin limits
 * @param minPt    Minimum jet pT for correction to be applied. If unspecified,
 * it only applies corrections for jets within the fit range of the function.
 */
void correctJets(std::vector<TLorentzVector>& jets,
                 std::vector<TF1>& corrFns,
                 std::vector<float>& etaBins,
                 float minPt);


/**
 * @brief Get current time & date
 * @return std::string with time & date
 */
std::string getCurrentTime();


/**
 * @brief Remove pattern from str
 * @details If str == pattern, it returns str to avoid an empty string.
 *
 * @param str String from which to remove the pattern.
 * @param pattern Regex pattern to remove from str
 * @return New TString with pattern removed from str
 */
TString removePattern(const TString & str, const TString & pattern);


/**
 * @brief Rescale jet energy fractions to account for the fact that they are
 * stored after JEC, but cuts apply *before* JEC.
 * @details JEC only affects the total energy, so we can just rescale by the
 * sum of energy fractions (which should = 1)
 */
void rescaleEnergyFractions(L1AnalysisRecoJetDataFormat * jets);


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 * Also applies JetID cuts.
 *
 * @param jets [description]
 * @param quality Can be LOOSE, TIGHT or TIGHTLEPVETO
 *
 * @return [description]
 */
std::vector<TLorentzVector> makeRecoTLorentzVectorsCleaned(const L1AnalysisRecoJetDataFormat & jets, std::string quality);


/**
 * @brief Loose JetID
 * @return bool If jet passed cuts or not
 */
bool looseCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);


/**
 * @brief Tight JetID
 * @return bool If jet passed cuts or not
 */
bool tightCleaning(float eta,
                   float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                   short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);


/**
 * @brief TightLepVeto JetID + custom muon multiplicity cut
 * @return bool If jet passed cuts or not
 */
bool tightLepVetoCleaning(float eta,
                          float chef, float nhef, float pef, float eef, float mef, float hfhef, float hfemef,
                          short chMult, short nhMult, short phMult, short elMult, short muMult, short hfhMult, short hfemMult);


/**
 * @brief Get index of jet in collection matching et/eta/phi
 * @details If not found, returns -1
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @param jets [description]
 * @return [description]
 */
template<typename T>
int findRecoJetIndex(T et, T eta, T phi, const L1AnalysisRecoJetDataFormat & jets);


/**
 * @brief Check if a certain trigger was fired.
 * @details Note, only checks to see if it was fired,
 * not if it was the *only* trigger that was fired.
 *
 * @param hlt Input vector of TStrings of tirgger names fired
 * @param selection Trigger name
 *
 * @return [description]
 */
bool checkTriggerFired(const std::vector<TString> & hlt, const std::string & selection);


/**
 * @brief Scalar sum of TLorentzVector pTs
 *
 * @param jets [description]
 * @return [description]
 */
float scalarSumPt(std::vector<TLorentzVector> jets);


/**
 * @brief Vector sum of TLorentzVector objects
 *
 * @param jets [description]
 * @return [description]
 */
TLorentzVector vectorSum(std::vector<TLorentzVector> jets);

#endif