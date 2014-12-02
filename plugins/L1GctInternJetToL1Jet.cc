// -*- C++ -*-
//
// Package:    L1Trigger/L1GctInternJetToL1Jet
// Class:      L1GctInternJetToL1Jet
// 
/**\class L1GctInternJetToL1Jet L1GctInternJetToL1Jet.cc L1Trigger/L1GctInternJetToL1Jet/plugins/L1GctInternJetToL1Jet.cc

 Description: EDProducer to turn L1GctInternJets into L1JetParticles. Output can then be passed into l1ExtraTreeProducer.

 Implementation:
      Fairly simple - get L1 GCT internal jet collection, loop through it, and for each jet create a L1JetParticle using
      info from the L1GctInternJetData and then store the L1JetParticle in a collection, which will be added to output.
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

#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"
#include "CondFormats/DataRecord/interface/L1CaloGeometryRecord.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/L1Trigger/interface/L1JetParticle.h"
#include "DataFormats/L1Trigger/interface/L1JetParticleFwd.h"

#include "DataFormats/L1GlobalCaloTrigger/interface/L1GctInternJetData.h"
#include "DataFormats/L1GlobalCaloTrigger/interface/L1GctCollections.h"

#include "CondFormats/L1TObjects/interface/L1CaloEtScale.h"
#include "CondFormats/DataRecord/interface/L1JetEtScaleRcd.h"
//
// class declaration
//

class L1GctInternJetToL1Jet : public edm::EDProducer {
    public:
        explicit L1GctInternJetToL1Jet(const edm::ParameterSet&);
        ~L1GctInternJetToL1Jet();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&) override;
        math::PtEtaPhiMLorentzVector gctInternJetToLorentzVector(
            const L1GctInternJetData& gctJet,
            const L1CaloGeometry& geom,
            const L1CaloEtScale& scale);

        // virtual void beginJob() override;
        // virtual void endJob() override;
        //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
        //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
        //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

        // ----------member data ---------------------------
        const edm::InputTag gctInternJetSource_;
        edm::EDGetTokenT<L1GctInternJetDataCollection> gctInternJetToken_;
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
L1GctInternJetToL1Jet::L1GctInternJetToL1Jet(const edm::ParameterSet& iConfig)
    : gctInternJetSource_( iConfig.getParameter< edm::InputTag >("gctInternJetSource") )
{
    using namespace l1extra ;

    //register your products
    produces<L1JetParticleCollection>("GctInternalJets");

    //now do what ever other initialization is needed
    gctInternJetToken_ = consumes<L1GctInternJetDataCollection>(gctInternJetSource_);

}


L1GctInternJetToL1Jet::~L1GctInternJetToL1Jet()
{
 
    // do anything here that needs to be done at desctruction time
    // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
/**
 * @brief Produces L1JetParticleCollection from L1GctInternJetDataCollection
 * @details [long description]
 *
 * @param iEvent [description]
 * @param iSetup [description]
 */
void
L1GctInternJetToL1Jet::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace l1extra ;
    using namespace std ;

    ESHandle< L1CaloGeometry > caloGeomESH ;
    iSetup.get< L1CaloGeometryRecord >().get( caloGeomESH ) ;
    const L1CaloGeometry* caloGeom = &( *caloGeomESH ) ;
    ESHandle< L1CaloEtScale > jetScale ;
    iSetup.get< L1JetEtScaleRcd >().get( jetScale ) ;


    // Get the L1GctInternJetDataCollection
    Handle<L1GctInternJetDataCollection> hwGctInternJetCollection;
    iEvent.getByToken(gctInternJetToken_, hwGctInternJetCollection);
    if (!hwGctInternJetCollection.isValid()) {
        throw cms::Exception("ProductNotValid") << "gctInternJetSource not valid";
    }

    auto_ptr< L1JetParticleCollection > gctInternJetColl( new L1JetParticleCollection );

    // Loop over each L1GctInternJetData obj, make a L1JetParticle obj from it
    L1GctInternJetDataCollection::const_iterator gctItr = hwGctInternJetCollection->begin();
    L1GctInternJetDataCollection::const_iterator gctEnd = hwGctInternJetCollection->end();
    for( ; gctItr != gctEnd ; ++gctItr) {
            if (!gctItr->empty() && (gctItr->et() != 0)){
                // cout << "Jet: " << gctItr->bx() << " : " << gctItr->rank() << " : " << gctItr->et() << " : "  << gctItr->eta() << " : " << gctItr->phi() << endl;
                gctInternJetColl->push_back(
                    L1JetParticle(gctInternJetToLorentzVector(*gctItr, *caloGeom, *jetScale),
                                  L1JetParticle::JetType::kUndefined,
                                  gctItr->bx())
                    );
        }
    }

    OrphanHandle< L1JetParticleCollection > gctInternJetHandle = iEvent.put(gctInternJetColl, "GctInternalJets");
}

/**
 * @brief Converts info in L1GctInternJetData to LorentzVector
 * @details [long description]
 *
 * @param gctJet Input gctJet
 * @param geom L1CaloGeometry to convert eta and phi into physical values
 * @param scale L1CaloEtScale to convert jet rank into physical ET
 * @return PolarLorentzVector (aka math::PtEtaPhiMLorentzVector) to use in L1JetParticle ctor
 */
math::PtEtaPhiMLorentzVector
L1GctInternJetToL1Jet::gctInternJetToLorentzVector(const L1GctInternJetData& gctJet,
                                                     const L1CaloGeometry& geom,
                                                     const L1CaloEtScale& scale) {
    // double et = gctJet.rank() * 0.5;
    // double et = gctJet.rank() * scale.linearLsb();
    double et = gctJet.et() * scale.linearLsb();
    double eta = geom.etaBinCenter(gctJet.regionId());
    double phi = geom.emJetPhiBinCenter(gctJet.regionId());
    double mass = 0.;
    // std::cout << et << " : "  << eta << " : " << phi << std::endl;
    return math::PtEtaPhiMLorentzVector(et, eta, phi, mass);
}

// ------------ method called once each job just before starting event loop  ------------
/*
void 
L1GctInternJetToL1Jet::beginJob()
{
}
*/

// ------------ method called once each job just after ending the event loop  ------------
/*
void 
L1GctInternJetToL1Jet::endJob() {
}
*/

// ------------ method called when starting to processes a run  ------------
/*
void
L1GctInternJetToL1Jet::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a run  ------------
/*
void
L1GctInternJetToL1Jet::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when starting to processes a luminosity block  ------------
/*
void
L1GctInternJetToL1Jet::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method called when ending the processing of a luminosity block  ------------
/*
void
L1GctInternJetToL1Jet::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/
 
// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
L1GctInternJetToL1Jet::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("gctInternJetSource", edm::InputTag("simGctDigis"))->setComment("Name of module that produces L1GctInternJetDataCollection");
  descriptions.add("L1GctInternJetToL1Jet", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(L1GctInternJetToL1Jet);
