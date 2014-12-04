// -*- C++ -*-
//
// Package:    L1Trigger/L1JetEnergyCorrections
// Class:      GenJetToL1Jet
// 
/**\class GenJetToL1Jet GenJetToL1Jet.cc L1Trigger/L1JetEnergyCorrections/plugins/GenJetToL1Jet.cc

 Description: EDProducer to turn GenJets into L1JetParticles. Can then be passed into l1ExtraTreeProducer

 Implementation:
      Fairly simple - get gen jet collection, loop through it, and for each jet create a L1JetParticle,
      and then store the L1JetParticle in a collection, which will be added to output.
*/
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Wed, 19 Nov 2014 22:13:47 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"

#include "DataFormats/JetReco/interface/GenJetCollection.h"

//
// class declaration
//

class GenJetToL1Jet : public edm::EDProducer {
    public:
        explicit GenJetToL1Jet(const edm::ParameterSet&);
        ~GenJetToL1Jet();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&) override;
        // virtual void beginJob() override;
        // virtual void endJob() override;
        //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
        //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

        // ----------member data ---------------------------
        const edm::InputTag genJetSource_;
        edm::EDGetTokenT<reco::GenJetCollection> genJetToken_;
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
GenJetToL1Jet::GenJetToL1Jet(const edm::ParameterSet& iConfig)
    : genJetSource_( iConfig.getParameter< edm::InputTag >("genJetSource") )
{
    using namespace l1extra ;

    //register your products
    produces< L1JetParticleCollection >( "GenJets" ) ;

    //now do what ever other initialization is needed
    genJetToken_ = consumes<reco::GenJetCollection>(genJetSource_);

}


GenJetToL1Jet::~GenJetToL1Jet()
{
 
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
/**
 * @brief Produces L1JetParticleCollection from GenJet collection
 * @details [long description]
 *
 * @param iEvent [description]
 * @param iSetup [description]
 */
void
GenJetToL1Jet::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace l1extra ;
    using namespace std ;

    // Get the GenJet collection
    Handle<reco::GenJetCollection> hwGenJetCollection;
    iEvent.getByToken(genJetToken_, hwGenJetCollection);
    if (!hwGenJetCollection.isValid()) {
        throw cms::Exception("ProductNotValid") << "genJetSource not valid";
    }

    auto_ptr< L1JetParticleCollection > genJetColl( new L1JetParticleCollection );

    // Loop over each L1GenJetData obj, make a L1JetParticle obj from it
    reco::GenJetCollection::const_iterator jetItr = hwGenJetCollection->begin();
    reco::GenJetCollection::const_iterator jetEnd = hwGenJetCollection->end();
    for( ; jetItr != jetEnd ; ++jetItr) {
        // cout << "Jet: " << jetItr->et() << " : "  << jetItr->eta() << " : " << jetItr->phi() << endl;
        genJetColl->push_back(L1JetParticle(jetItr->p4(), L1JetParticle::JetType::kUndefined, 0));
    }

    OrphanHandle< L1JetParticleCollection > genJetHandle = iEvent.put(genJetColl, "GenJets");
}

// ------------ method called once each job just before starting event loop  ------------
/*
void 
GenJetToL1Jet::beginJob()
{
}
*/

// ------------ method called once each job just after ending the event loop  ------------
/*
void 
GenJetToL1Jet::endJob() {
}
*/

// ------------ method called when starting to processes a run  ------------
/*
void
GenJetToL1Jet::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
GenJetToL1Jet::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
GenJetToL1Jet::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
GenJetToL1Jet::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenJetToL1Jet::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("genJetSource", edm::InputTag("ak5GenJets"))->setComment("Name of module that produces GenJet collection (e.g. ak5GenJets)");
  descriptions.add("GenJetToL1Jet", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenJetToL1Jet);
