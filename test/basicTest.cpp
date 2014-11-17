#include <memory>
#include <cppunit/TestFixture.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include <cppunit/ui/text/TestRunner.h>
#include <cppunit/CompilerOutputter.h>
#include <cppunit/TestCase.h>
#include <cppunit/extensions/HelperMacros.h>

/**
 * @brief An example of how to implement CppUnit, since the cookbook is confusing.
 * @details To ensure tests are build & run you need to do:
 * - make sure test in "test" folder
 * - add to test/BuildFile.xml:
 * <use name="cppunit"/>
 * <bin name="BasicTest" file="basicTest.cpp"/>
 * - to build & run do: scram b runtests
 */

class BasicTest : public CppUnit::TestCase {

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
    CPPUNIT_TEST_SUITE( BasicTest );
    CPPUNIT_TEST( runPassingTest );
    CPPUNIT_TEST( runFailingTest );
    CPPUNIT_TEST_SUITE_END();

public:
    BasicTest() {};

    void setUp();
    void tearDown();

    void runPassingTest();
    void runFailingTest();

private:
    std::vector<double> v;

};

CPPUNIT_TEST_SUITE_NAMED_REGISTRATION( BasicTest, "BasicTest" );

// use setUp() and tearDown() to setup/destroy common objects used for tests
void BasicTest::setUp() {
    v.push_back(1);
    v.push_back(2);
    v.push_back(3);
}

void BasicTest::tearDown() {
}

void BasicTest::runPassingTest() {
    CPPUNIT_ASSERT( v.size() == 3 );
    CPPUNIT_ASSERT( v.at(0) == 1 );
}

void BasicTest::runFailingTest() {
    CPPUNIT_ASSERT( v.at(1) == 1 );
}


int main() {
    /**
     * You can run your tests simply like this, in which case your test class (BasicTest)
     * needs to inherit from CppUnit::TestCase
     */
    // BasicTest b;
    // b.runPassingTest();
    /**
     * This last test fails when you compile & run - will throw a CppUnit exception e.g.
     * an instance of 'CppUnit::Exception'
     * what():  assertion failed
     * - Expression: 1+2 == 3+1
     */
    // b.runFailingTest();

    /**
     * A TestRunner runs your tests and collects the results. It needs a
     * CppUnit::TestSuite, which your test class returns via static method suite. This
     * is all done via the macros used in the class above.
     */
    CppUnit::TextUi::TestRunner runner;
    runner.addTest( BasicTest::suite() );
    // runner.run();
    // return 0;

    // alternatively, to include in BuildProcess, have to return value
    // diff to 0 in event of Failure
    bool wasSuccessful = runner.run("", false);
    return !wasSuccessful;
}