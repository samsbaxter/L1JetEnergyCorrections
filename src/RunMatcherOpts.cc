// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     RunMatcherOpts
// 
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Fri, 28 Nov 2014 14:26:39 GMT
//
#include "RunMatcherOpts.h"

// system include files
#include <iostream>

// ROOT include files
#include "TString.h"

// BOOST include
#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>

// user include files

using std::cout;
using std::endl;

//
// constants, enums and typedefs
//

//
// static data member definitions
//


/////////////////////////////////
// constructors and destructor //
/////////////////////////////////
RunMatcherOpts::RunMatcherOpts(int argc, char* argv[]):
    input_(""),
    refDir_(""),
    l1Dir_(""),
    output_(""),
    nEvents_(0),
    drawN_(0)
{
    namespace po = boost::program_options;
    namespace fs = boost::filesystem;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("help,h", "produce help message & exit")
        ("nEvents,N",
            po::value<int>(&nEvents_)->default_value(-1),
            "number of events to run over. -1 for all.")
        ("input,I",
            po::value<std::string>(&input_)->default_value("python/L1Tree.root"),
            "input filename")
        ("refDir",
            po::value<std::string>(&refDir_)->default_value("l1ExtraTreeProducerGenAk5"),
            "reference jet TDirectory in input file")
        ("refBranches",
            po::value<std::vector<std::string>>(&refJetBranchNames_)->multitoken()->default_value(std::vector<std::string>(1,"cenJet"), "cenJet"),
            "reference jet branches in TTree (e.g. cenJet)")
        ("l1Dir",
            po::value<std::string>(&l1Dir_)->default_value("l1ExtraTreeProducerGctIntern"),
            "L1 jet TDirectory in input file")
        ("l1Branches",
            po::value<std::vector<std::string>>(&l1JetBranchNames_)->multitoken()->default_value(std::vector<std::string>(1,"cenJet"), "cenJet"),
            "l1 jet branches in TTree (e.g. cenJet)")
        ("output,O",
            po::value<std::string>(&output_)->default_value("pairs.root"),
            "output filename")
        ("draw,d",
            po::value<int>(&drawN_)->default_value(10),
            "number of events to draw 2D eta-phi plot of ref, L1 & matched " \
            "jets (for debugging). PLots saved in $PWD/match_plots." \
            " 0 for no plots.")
    ;
    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
    } catch (const boost::program_options::unknown_option& e){
        cout << "Unrecognised option " << e.what() << endl;
        cout << desc << endl;
        std::exit(1);
    } catch (const boost::program_options::invalid_option_value& e){
        cout << "Invalid value for option " << e.what() << endl;
        cout << desc << endl;
        std::exit(1);
    }

    po::notify(vm);

    if (vm.count("help")) {
        cout << desc << endl;
        std::exit(1);
    }

}

// RunMatcherOpts::RunMatcherOpts(const RunMatcherOpts& rhs)
// {
//    // do actual copying here;
// }

RunMatcherOpts::~RunMatcherOpts()
{
}

//
// assignment operators
//
// const RunMatcherOpts& RunMatcherOpts::operator=(const RunMatcherOpts& rhs)
// {
//   //An exception safe implementation is
//   RunMatcherOpts temp(rhs);
//   swap(rhs);
//
//   return *this;
// }

//
// member functions
//

//
// const member functions
//

//
// static member functions
//
