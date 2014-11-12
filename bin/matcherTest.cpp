#include "DeltaR_Matcher.h"
#include <iostream>

int main() {
    std::cout << "Matching test" << std::endl;
    DeltaR_Matcher * m = new DeltaR_Matcher(0.5);
    m->printDeltaR();
}