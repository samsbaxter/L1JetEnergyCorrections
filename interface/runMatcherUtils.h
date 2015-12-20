#ifndef L1Trigger_L1JetEnergyCorrections_runMatcherUtils_h
#define L1Trigger_L1JetEnergyCorrections_runMatcherUtils_h

// STL headers
#include <vector>

// ROOT headers
#include "TLorentzVector.h"
#include "TF1.h"
#include "TString.h"


/**
 * @brief Make a std::vector of TLorentzVectors out of input vectors of et, eta, phi.
 *
 * @param et [description]
 * @param eta [description]
 * @param phi [description]
 * @return [description]
 */
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<float> et,
                                                std::vector<float> eta,
                                                std::vector<float> phi);


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
std::vector<TLorentzVector> makeTLorentzVectors(std::vector<float> et,
                                                std::vector<float> eta,
                                                std::vector<float> phi,
                                                std::vector<short> bx);


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

#endif