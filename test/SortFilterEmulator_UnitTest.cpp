#include <iostream>
#include <memory>
#include <vector>
#include <algorithm>

#include <cppunit/TestFixture.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/ui/text/TestRunner.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/TestCase.h>
#include <cppunit/extensions/HelperMacros.h>

#include "TLorentzVector.h"
#include "SortFilterEmulator.h"

using std::vector;
using std::cout;
using std::endl;

/**
 * @brief Unit tests for SortFilterEmulator class
 * @details To build and run, do:
 * scram b runtests
 * To turn on/off print statments, change the printStatments bool in setUp()
 */
class SortFilterEmulator_UnitTest : public CppUnit::TestCase {

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
    CPPUNIT_TEST_SUITE( SortFilterEmulator_UnitTest );
    CPPUNIT_TEST( lotsJets );
    CPPUNIT_TEST( noCenJets );
    CPPUNIT_TEST( noFwdJets );
    CPPUNIT_TEST( fewJets );
    CPPUNIT_TEST_SUITE_END();

public:
    SortFilterEmulator_UnitTest() {};

    void setUp();
    void tearDown();

    // Tests
    void lotsJets();
    void noCenJets();
    void noFwdJets();
    void fewJets();

private:
    bool printStatements;
    std::vector<TLorentzVector> jets; // input
    SortFilterEmulator * emu;
    std::vector<TLorentzVector> allJets; // outputs
    std::vector<TLorentzVector> cenJets;
    std::vector<TLorentzVector> fwdJets;
};

// CPPUNIT_TEST_SUITE_NAMED_REGISTRATION( SortFilterEmulator_UnitTest, "SortFilterEmulator_UnitTest" );

/**
 * @brief Setup common objects used for tests, at start of each CPPUNIT_TEST
 */
void SortFilterEmulator_UnitTest::setUp() {
    printStatements = false;
}


/**
 * @brief Destroy any common objects used for tests, at end of each CPPUNIT_TEST
 */
void SortFilterEmulator_UnitTest::tearDown() {
    if (emu != nullptr) delete emu;
    if (jets.size() != 0) jets.clear();
    if (allJets.size() != 0) allJets.clear();
    if (cenJets.size() != 0) cenJets.clear();
    if (fwdJets.size() != 0) fwdJets.clear();
}


/**
 * @brief Throw lots of jets at emulator.
 */
void SortFilterEmulator_UnitTest::lotsJets() {

    TLorentzVector c1; c1.SetPtEtaPhiM(40, 0.1, 0.1, 0.0);
    TLorentzVector c2; c2.SetPtEtaPhiM(50, 0.2, -0.1, 0.0);
    TLorentzVector c3; c3.SetPtEtaPhiM(60, 0.3, 0.2, 0.0);
    TLorentzVector c4; c4.SetPtEtaPhiM(70, 0.4, -0.3, 0.0);
    TLorentzVector c5; c5.SetPtEtaPhiM(80, 0.5, 0.4, 0.0);
    TLorentzVector f1; f1.SetPtEtaPhiM(41, 3.1, 0.1, 0.0);
    TLorentzVector f2; f2.SetPtEtaPhiM(52, 3.2, -0.1, 0.0);
    TLorentzVector f3; f3.SetPtEtaPhiM(63, 4.3, 0.2, 0.0);
    TLorentzVector f4; f4.SetPtEtaPhiM(74, 4.4, -0.3, 0.0);
    TLorentzVector f5; f5.SetPtEtaPhiM(85, 4.5, 0.4, 0.0);
    jets = {c2, f1, c3, f2, f4, c5, c1, f3, c4, f5};

    unsigned nMax = 4;
    emu = new SortFilterEmulator(nMax);
    emu->setJets(jets);
    allJets = emu->getAllJets();
    cenJets = emu->getCenJets();
    fwdJets = emu->getFwdJets();

    vector<TLorentzVector> allProper = {c5, c4, c3, c2, f5, f4, f3, f2};
    vector<TLorentzVector> cenProper = {c5, c4, c3, c2};
    vector<TLorentzVector> fwdProper = {f5, f4, f3, f2};

    CPPUNIT_ASSERT( allJets == allProper );
    CPPUNIT_ASSERT( cenJets == cenProper );
    CPPUNIT_ASSERT( fwdJets == fwdProper );

}

/**
 * @brief No cen jets
 * @details [long description]
 */
void SortFilterEmulator_UnitTest::noCenJets() {
    TLorentzVector f1; f1.SetPtEtaPhiM(41, 3.1, 0.1, 0.0);
    TLorentzVector f2; f2.SetPtEtaPhiM(52, 3.2, -0.1, 0.0);
    TLorentzVector f3; f3.SetPtEtaPhiM(63, 4.3, 0.2, 0.0);
    TLorentzVector f4; f4.SetPtEtaPhiM(74, 4.4, -0.3, 0.0);
    TLorentzVector f5; f5.SetPtEtaPhiM(85, 4.5, 0.4, 0.0);
    jets = {f1, f2, f4, f3, f5};

    unsigned nMax = 4;
    emu = new SortFilterEmulator(nMax);
    emu->setJets(jets);
    allJets = emu->getAllJets();
    cenJets = emu->getCenJets();
    fwdJets = emu->getFwdJets();

    vector<TLorentzVector> allProper = {f5, f4, f3, f2};
    vector<TLorentzVector> cenProper = {};
    vector<TLorentzVector> fwdProper = {f5, f4, f3, f2};

    CPPUNIT_ASSERT( allJets == allProper );
    CPPUNIT_ASSERT( cenJets == cenProper );
    CPPUNIT_ASSERT( fwdJets == fwdProper );

}

/**
 * @brief No fwd jets
 * @details [long description]
 */
void SortFilterEmulator_UnitTest::noFwdJets() {
    TLorentzVector c1; c1.SetPtEtaPhiM(40, 0.1, 0.1, 0.0);
    TLorentzVector c2; c2.SetPtEtaPhiM(50, 0.2, -0.1, 0.0);
    TLorentzVector c3; c3.SetPtEtaPhiM(60, 0.3, 0.2, 0.0);
    TLorentzVector c4; c4.SetPtEtaPhiM(70, 0.4, -0.3, 0.0);
    TLorentzVector c5; c5.SetPtEtaPhiM(80, 0.5, 0.4, 0.0);
    jets = {c2, c3, c5, c1, c4};

    unsigned nMax = 4;
    emu = new SortFilterEmulator(nMax);
    emu->setJets(jets);
    allJets = emu->getAllJets();
    cenJets = emu->getCenJets();
    fwdJets = emu->getFwdJets();

    vector<TLorentzVector> allProper = {c5, c4, c3, c2};
    vector<TLorentzVector> cenProper = {c5, c4, c3, c2};
    vector<TLorentzVector> fwdProper = {};

    CPPUNIT_ASSERT( allJets == allProper );
    CPPUNIT_ASSERT( cenJets == cenProper );
    CPPUNIT_ASSERT( fwdJets == fwdProper );

}

/**
 * @brief number of jets < nMax
 * @details [long description]
 */
void SortFilterEmulator_UnitTest::fewJets() {

    TLorentzVector c1; c1.SetPtEtaPhiM(40, 0.1, 0.1, 0.0);
    TLorentzVector c2; c2.SetPtEtaPhiM(50, 0.2, -0.1, 0.0);
    TLorentzVector c3; c3.SetPtEtaPhiM(60, 0.3, 0.2, 0.0);
    TLorentzVector f1; f1.SetPtEtaPhiM(41, 3.1, 0.1, 0.0);
    TLorentzVector f2; f2.SetPtEtaPhiM(52, 3.2, -0.1, 0.0);
    jets = {c2, f1, c3, f2, c1};

    unsigned nMax = 4;
    emu = new SortFilterEmulator(nMax);
    emu->setJets(jets);
    allJets = emu->getAllJets();
    cenJets = emu->getCenJets();
    fwdJets = emu->getFwdJets();

    vector<TLorentzVector> allProper = {c3, c2, c1, f2, f1};
    vector<TLorentzVector> cenProper = {c3, c2, c1};
    vector<TLorentzVector> fwdProper = {f2, f1};

    CPPUNIT_ASSERT( allJets == allProper );
    CPPUNIT_ASSERT( cenJets == cenProper );
    CPPUNIT_ASSERT( fwdJets == fwdProper );

}

/**
 * @brief Main routine that runs the tests and output the results to screen.
 */
int main() {
    /**
     * A TestRunner runs your tests and collects the results. It needs a
     * CppUnit::TestSuite, which your test class returns via static method suite. This
     * is all done via the macros used in the class above.
     */
    CppUnit::TextUi::TestRunner runner;
    runner.addTest( SortFilterEmulator_UnitTest::suite() );
    runner.run();
    return 0;

    // alternatively, to include in BuildProcess, have to return value
    // diff to 0 in event of Failure
    // bool wasSuccessful = runner.run("", false);
    // return !wasSuccessful;
}