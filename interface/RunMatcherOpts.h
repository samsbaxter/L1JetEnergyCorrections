#ifndef L1Trigger_L1JetEnergyCorrections_RunMatcherOpts_h
#define L1Trigger_L1JetEnergyCorrections_RunMatcherOpts_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     RunMatcherOpts
// 
/**\class RunMatcherOpts RunMatcherOpts.h "interface/RunMatcherOpts.h"

 Description: Class to deal with command-line options for RunMatcher program

 Usage:
     int main(int argc, char* argv[]) {
            RunMatcherOpts opts(arc, argv);
            std::string fName = opts.intputFilename();
     }

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Fri, 28 Nov 2014 14:26:39 GMT
//

// system include files
#include <string>
#include <vector>

// user include files

// forward declarations
class TString;

/**
 * @brief Class to deal with command-line options for RunMatcher program
 * @details Based on boost:program_options
 *
 * @param argc Pass from main(int argc, char** argv)
 * @param argv Pass from main(int argc, char** argv)
 */
class RunMatcherOpts
{

    public:
        /**
         * @brief Constructor, parses command line options
         *
         * @param argc Pass from main(int argc, char** argv)
         * @param argv Pass from main(int argc, char** argv)
         */
        RunMatcherOpts(int argc, char* argv[]);

        /**
         * @brief Destrcutor
         */
        virtual ~RunMatcherOpts();

        // ---------- const member functions ---------------------

        // ---------- static member functions --------------------

        // ---------- member functions ---------------------------

        /**
         * @brief Get input ROOT filename
         */
        std::string inputFilename() { return input_; };

        /**
         * @brief Get name of TDirectory that holds reference jets
         */
        std::string refJetDirectory() { return refDir_; };

        /**
         * @brief Get name of TDirectory that holds L1 jets
         */
        std::string l1JetDirectory() { return l1Dir_; };

        /**
         * @brief Get output ROOT filename
         */
        std::string outputFilename() { return output_; };

        /**
         * @brief Get number of events to plot
         */
        int drawNumber() { return drawN_; };

        /**
         * @brief Get number of events to run over
         */
        int nEvents() { return nEvents_; };

        /**
         * @brief Get TBranch names for ref jets
         * @details Only need stem, e.g. cenJet
         */
        std::vector<std::string> refJetBranchNames() { return refJetBranchNames_; };

        /**
         * @brief Get TBranch names for L1 jets
         * @details Only need stem, e.g. cenJet
         */
        std::vector<std::string> l1JetBranchNames() { return l1JetBranchNames_; };

    private:
        RunMatcherOpts(const RunMatcherOpts&); // stop default

        const RunMatcherOpts& operator=(const RunMatcherOpts&); // stop default

        // ---------- member data --------------------------------
        std::string input_, refDir_, l1Dir_, output_;
        int nEvents_, drawN_;
        std::vector<std::string> refJetBranchNames_, l1JetBranchNames_;
};


#endif
