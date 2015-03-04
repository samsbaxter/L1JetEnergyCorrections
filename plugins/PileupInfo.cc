// -*- C++ -*-
//
// Package:    L1Trigger/L1JetEnergyCorrections
// Class:      PileupInfo
// 
/**\class PileupInfo PileupInfo.cc L1Trigger/L1JetEnergyCorrections/plugins/PileupInfo.cc

 Description: To store info about pileup, eg. number of vertices

 Implementation:
      [Notes on implementation]
*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 04 Mar 2015 15:28:31 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "TTree.h"

using std::vector;

//
// class declaration
//

class PileupInfo : public edm::EDAnalyzer {
    public:
        explicit PileupInfo(const edm::ParameterSet&);
        ~PileupInfo();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


    private:
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        // virtual void beginJob() override;
        // virtual void endJob() override;

        //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
        //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

        // ----------member data ---------------------------
        const edm::InputTag pileupInfoSource_;
        edm::EDGetTokenT<vector<PileupSummaryInfo>> pileupInfoToken_;
        // output file
        edm::Service<TFileService> fs_;
        // tree
        TTree * tree_;

        // things to store in branches
        float trueNumInteractions_;
        int num_PU_vertices_;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
PileupInfo::PileupInfo(const edm::ParameterSet& iConfig):
    pileupInfoSource_( iConfig.getParameter< edm::InputTag >("pileupInfoSource") ),
    trueNumInteractions_(-1.),
    num_PU_vertices_(-1)
{
    // setup token
    pileupInfoToken_ = consumes<vector<PileupSummaryInfo>>(pileupInfoSource_);

    // setup tree & branches
    tree_ = fs_->make<TTree>("PileupInfo", "PileupInfo");
    tree_->Branch("TrueNumInteractions", &trueNumInteractions_);
    tree_->Branch("NumPUVertices", &num_PU_vertices_);
}


PileupInfo::~PileupInfo()
{
 
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
PileupInfo::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;

    // Get the PileupSummaryInfo vector
    Handle<vector<PileupSummaryInfo>> puInfoCollection;
    iEvent.getByToken(pileupInfoToken_, puInfoCollection);
    if (!puInfoCollection.isValid()) {
        throw cms::Exception("ProductNotValid") << "pileupInfoSource not valid";
    }

    // reset vars
    trueNumInteractions_ = -1.;
    num_PU_vertices_ = -1;

    // Loop over vector, find in-time entry, then store the relevant info
    vector<PileupSummaryInfo>::const_iterator puItr = puInfoCollection->begin();
    vector<PileupSummaryInfo>::const_iterator puEnd = puInfoCollection->end();
    for( ; puItr != puEnd; ++puItr) {
        int bx = puItr->getBunchCrossing();
        if (bx == 0) {
            trueNumInteractions_ = puItr->getTrueNumInteractions();
            num_PU_vertices_ = puItr->getPU_NumInteractions();
            break;
        }
    }

    tree_->Fill();

}


// ------------ method called once each job just before starting event loop  ------------
/*
void 
PileupInfo::beginJob()
{
}
*/

// ------------ method called once each job just after ending the event loop  ------------
/*
void 
PileupInfo::endJob() 
{
}
*/

// ------------ method called when starting to processes a run  ------------
/*
void 
PileupInfo::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void 
PileupInfo::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void 
PileupInfo::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void 
PileupInfo::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PileupInfo::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("pileupInfoSource", edm::InputTag("addPileupInfo"))->setComment("Name of module with PileupSummaryInfo objects");
  descriptions.add("PileupInfo", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PileupInfo);
