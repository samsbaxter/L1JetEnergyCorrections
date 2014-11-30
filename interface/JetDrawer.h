#ifndef L1Trigger_L1JetEnergyCorrections_JetDrawer_h
#define L1Trigger_L1JetEnergyCorrections_JetDrawer_h
// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     JetDrawer
// 
/**\class JetDrawer JetDrawer.h "interface/JetDrawer.h"

 Description: Class to draw ref jets, L1 jets, and matched pairs. Useful for debugging.

 Usage:
     JetDrawer jd(refJets, l1Jets, matchedJets);
     drawer.drawAndSave("plots/myplot.pdf");

*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Sat, 29 Nov 2014 11:46:23 GMT
//

// system include files
#include <vector>
#include <iostream>

// user include files
#include "TLorentzVector.h"
#include "TGraph.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TPaveText.h"
#include "TText.h"

/**
 * @brief Class to draw reference jets, L1 jets, & matching pairs on a plot.
 * Useful for debugging/checking matching works correctly.
 */
class JetDrawer
{

    public:
        /**
         * @brief Ctor that makes TMultiGraph and TLegend from input collections.
         *
         * @param refJets reference jet collection
         * @param l1Jets l1 jet collection
         * @param matchedJets pairs of matched jets (e.g. from Matcher::getMatchingPairs())
         */
        JetDrawer(std::vector<TLorentzVector> refJets,
                 std::vector<TLorentzVector> l1Jets,
                 std::vector<std::pair<TLorentzVector,TLorentzVector>> matchedJets,
                 TString labelText="");

        virtual ~JetDrawer();

        // ---------- const member functions ---------------------

        // ---------- static member functions --------------------

        // ---------- member functions ---------------------------

        /**
         * @brief Draw graph and legend on canvas and save to file
         *
         * @param filename Filepath & name to save canvas as.
         */
        virtual void drawAndSave(TString filename);

        /**
         * @brief Draw graph and save to TFile
         *
         * @param file TFile to save graph in
         */
        virtual void drawAndSave(TFile * file);

        /**
         * @brief Access multigraph with graphs for ref jets, l1 jets, & matched jets
         */
        virtual TMultiGraph * getGraph() const { return graph_; };

        /**
         * @brief Access TLegend
         */
        virtual TLegend * getLegend() const { return legend_; };

        /**
         * @brief Access TCanvas on which plot & legend are drawn
         */
        virtual TCanvas * getCanvas() const { return canvas_; };

    private:
        JetDrawer(const JetDrawer&); // stop default

        const JetDrawer& operator=(const JetDrawer&); // stop default

        /**
         * @brief Make TMultiGraph from jet collections
         * @details [long description]
         * @return Returns TMultiGraph with 3 TGraphs named,
         * "refJetGraph", "l1JetGraph" & "matchedJetGraph"
         */
        TMultiGraph * makeGraph();

        /**
         * @brief Apply style to ref jet graph
         */
        void styleRefJetGraph(TGraph * graph);

        /**
         * @brief Apply style to l1 jet graph
         */
        void styleL1JetGraph(TGraph * graph);

        /**
         * @brief Apply style to matched jet graph
         */
        void styleMatchedJetGraph(TGraph * graph);

        /**
         * @brief Make a legend for the plot
         * @details Generally put legend at top
         * @return TLegend to be used in final drawing
         */
        TLegend * makeLegend();

        /**
         * @brief Check we can write to path. Will overwrite file if
         * already exists
         * @details Checks that parent directory isn't a file, and can be
         * created (if it doens't already exist)
         *
         * @param path Path of file
         * @return True if OK, false otherwise
         */
        bool checkPath(std::string filepath);

        // ---------- member data --------------------------------
        const std::vector<TLorentzVector> refJets_;
        const std::vector<TLorentzVector> l1Jets_;
        const std::vector<std::pair<TLorentzVector,TLorentzVector>> matchedJets_;
        TMultiGraph * graph_;
        TGraph * refJetGraph_, * l1JetGraph_, * matchedJetGraph_;
        TLegend * legend_;
        TCanvas * canvas_;
        TPaveText * label_;
        TString labelText_;
};


#endif
