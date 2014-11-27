#include <iostream>
#include <exception>

#include "TFile.h"
#include "TROOT.h"

using namespace std;

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

    if (mode == "") {
        mode = "READ";
    }

    TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject(filename);
    if (!f || !f->IsOpen()) {
        f = new TFile(filename, mode);
    } else {
        throw "Couldn't open "+filename;
    }

    // did it actually open correctly?
    if (!f->IsZombie()) {
        std::cout << "Opened " + filename << " in " << mode << " mode" << std::endl;
        return f;
    } else {
        throw "Couldn't open "+filename;
    }
}


TTree* loadTree(TFile * f, TString treeName) {
    return (TTree*) f->Get(treeName);
}