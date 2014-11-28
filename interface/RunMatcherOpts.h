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
     }

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Fri, 28 Nov 2014 14:26:39 GMT
//

// system include files

// user include files

// forward declarations
class TString;

class RunMatcherOpts
{

    public:
        RunMatcherOpts(int argc, char* argv[]);
        virtual ~RunMatcherOpts();

        // ---------- const member functions ---------------------

        // ---------- static member functions --------------------

        // ---------- member functions ---------------------------
        std::string inputFilename() { return input_; };
        std::string refJetDirectory() { return refDir_; };
        std::string l1JetDirectory() { return l1Dir_; };
        std::string outputFilename() { return output_; };
        int drawNumber() { return drawN_; };
        int nEvents() { return nEvents_; };

    private:
        RunMatcherOpts(const RunMatcherOpts&); // stop default

        const RunMatcherOpts& operator=(const RunMatcherOpts&); // stop default

        // ---------- member data --------------------------------
        std::string input_, refDir_, l1Dir_, output_;
        int nEvents_, drawN_;
};


#endif
