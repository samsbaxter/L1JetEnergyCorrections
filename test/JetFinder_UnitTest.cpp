#include <memory>
#include <cppunit/TestFixture.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/ui/text/TestRunner.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/TestCase.h>
#include <cppunit/extensions/HelperMacros.h>

#include "L1Trigger/L1TCalorimeter/interface/Stage2MainProcessor.h"
#include "L1Trigger/L1TCalorimeter/interface/Stage2Layer2JetAlgorithmFirmware.h"
#include "L1Trigger/L1TCalorimeter/interface/CaloParamsHelper.h"
#include "DataFormats/L1TCalorimeter/interface/CaloTower.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "L1Trigger/L1TCalorimeter/interface/CaloTools.h"


using std::cout;
using std::endl;


// External equality and inequality operators, as not defined for CaloTower
bool operator==(const l1t::CaloTower &tower1, const l1t::CaloTower &tower2) {
    return ((tower1.hwPt() == tower2.hwPt()) && (tower1.hwEta() == tower2.hwEta()) && (tower1.hwPhi() == tower2.hwPhi()));
}


bool operator!=(const l1t::CaloTower &tower1, const l1t::CaloTower &tower2) {
    return !((tower1.hwPt() == tower2.hwPt()) && (tower1.hwEta() == tower2.hwEta()) && (tower1.hwPhi() == tower2.hwPhi()));
}


class JetFinderTest : public CppUnit::TestCase {

    /**
     * CppUnit provides a TestSuite class that runs any number of TestCases together.
     * In this case, you'll want your test class to inherit from CppUnit::TestFixture
     *
     * These macros saves a lot of typing - basically registers a TestSuite, and
     * attaches tests to suite.
     *
     * Make sure you put these before the other function declarations, otherwise it'll
     * complain about setUp() being private.
     */
    CPPUNIT_TEST_SUITE( JetFinderTest );
    CPPUNIT_TEST( paramsForStage2 );
    CPPUNIT_TEST( test_getTower );
    CPPUNIT_TEST( makeTowerCollection );
    CPPUNIT_TEST_SUITE_END();

public:
    JetFinderTest() {};

    void setUp();
    void tearDown();

    void paramsForStage2();
    void setupJetFinder();
    void test_getTower();
    void makeTowerCollection();

private:
    l1t::CaloParamsHelper m_params;
    l1t::Stage2Layer2JetAlgorithm * m_jetAlgo;
};

// CPPUNIT_TEST_SUITE_REGISTRATION( JetFinderTest, "JetFinderTest" );

// use setUp() and tearDown() to setup/destroy common objects used for tests
void JetFinderTest::setUp() {
    m_params.setJetLsb(0.5);
    m_params.setJetSeedThreshold(1.5);
    m_params.setJetPUSType("ChunkyDonut");
    m_params.setJetCalibrationType("None");
}

void JetFinderTest::tearDown() {
    if (m_jetAlgo) delete m_jetAlgo;
}

void JetFinderTest::paramsForStage2() {
    CPPUNIT_ASSERT( m_params.isValidForStage2() );
    CPPUNIT_ASSERT( m_params.jetLsb() == 0.5 );
}

void JetFinderTest::setupJetFinder() {
    m_jetAlgo = new l1t::Stage2Layer2JetAlgorithmFirmwareImp1(&m_params);
}

void JetFinderTest::test_getTower() {
    math::XYZTLorentzVector p4;
    l1t::CaloTower tower(p4, 10, 10, 12, 1, 1, 0, 5, 5, 1);
    std::vector<l1t::CaloTower> towers = {tower};
    const l1t::CaloTower& towGood = l1t::CaloTools::getTower(towers, 1, 1);
    CPPUNIT_ASSERT( towGood == tower );
    const l1t::CaloTower& towBad = l1t::CaloTools::getTower(towers, 1, 11);
    CPPUNIT_ASSERT_ASSERTION_FAIL( CPPUNIT_ASSERT( towBad == tower ) );
}


void JetFinderTest::makeTowerCollection() {

    // for (int i = 0; i < l1t::CaloTools::kHBHENrPhi; ++i) {
    //     if (energies[i].size() != l1t::CaloTools::kHFEnd) {
    //         cout << "Wrong size " << energies[i].size() << endl;
    //     }
    // }
    CPPUNIT_ASSERT( 1 == 1 );
}

int main() {
    /**
     * A TestRunner runs your tests and collects the results. It needs a
     * CppUnit::TestSuite, which your test class returns via static method suite. This
     * is all done via the macros used in the class above.
     */
    CppUnit::TextUi::TestRunner runner;
    runner.addTest( JetFinderTest::suite() );
    runner.run();
    return 0;
}