#include <iostream>
#include <exception>
#include <stdexcept>

#include "TFile.h"
#include "TROOT.h"

using std::cout;
using std::endl;

/**
 * This file contains common functions to be used in programs, e.g. opening files safely
 *
 * Robin Aggleton 25/11/14
 */

// TODO: put in namespace?

/**
 * @brief Open ROOT file safely
 * @details Designed to encapsulate error checking on file
 *
 * @param filename ROOT filename
 * @param mode Option to open file - see http://root.cern.ch/root/html/TFile.html#TFile:TFile@2.
 * If unspecified, defaults to READ.
 *
 * @return Pointer to TFile.
 */
TFile* openFile(TString filename, TString mode="") {
    // check user args
    if (filename == "") {
        throw std::invalid_argument("filename is null - cannot open ROOT file");
    }

    // safe default mode
    if (mode == "") {
        mode = "READ";
    }

    // actually try and open the file
    TFile *f = dynamic_cast<TFile*>(gROOT->GetListOfFiles()->FindObject(filename));
    if (!f || !f->IsOpen()) {
        f = new TFile(filename, mode);
    } else {
        throw std::runtime_error(("Couldn't open "+filename).Data());
    }

    // did it actually open correctly?
    if (!f->IsZombie()) {
        cout << "Opened " << filename << " in " << mode << " mode" << endl;
        return f;
    } else {
        throw std::runtime_error(("Couldn't open "+filename).Data());
    }
}


/**
 * @brief Get TTree from TFile
 * @details Encapsulates error checking.
 *
 * @param f TFile to get TTree from
 * @param treeName Name of TTree
 *
 * @return The TTree wanted
 */
TTree* loadTree(TFile * f, TString treeName) {
    return dynamic_cast<TTree*>(f->Get(treeName));
}