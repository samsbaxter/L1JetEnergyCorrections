# Notes for development on L1JetEnergyCorrections

## Derivations/Specialisation

The objects mentioned in [README](README.md) (Matcher, Calibration calculator) are all **interfaces** (i.e abstract classes). Subclasses/derived classes of these actually perform the matching or calibrating *for some particular matching/calibration scheme*. This way, there is a unified interface, so one can easily swap in a different way of matching or calibrating without a) worrying that they're replacing the right parts/missing bits and b) mucking up some other bit of code.

It's trying to avoid some 1000 line ROOT script where all the important procedures are hidden away, and are coupled to some particular setup.

**NOTE**: currently the Calibration bit hasn't been class-ified. It will probably be needed at somepoint, but it's pretty short.

## An example

One type of jet matching is by deltaR(ref jet - L1 jet), where deltaR^2 = deltaEta^2 + deltaPhi^2 (all deltas are between ref and L1 jets). This is implemented in DeltaR_Matcher.

One type of calibration scheme is by plotting the ratio of E_T for matched reference and L1 jets, and fitting with a particular function. This is shown in XXX.

## I want to do X

- **I want to make a new program**: write your C++ program in `/bin`, then add a line to [BuildFile.xml](bin/BuildFile.xml) like:
```
<bin name="myProgName" file="myProg.cpp"/>
```
Also remember to add any addtional includes.


##Misc notes

### L1ExtraTree
This is the interface to the L1ExtraTree TTree that is produced by the L1Ntuples. It's not great - it's aslight modification to the output from tree.MakeClass(). It would be better if it were more structured, had more protections in place, & fewer exposed variables.

### RunMatcherOpts
This parses user arguments to the RunMatcher program. Based on boost's program_options class. Not very fancy, but does the job.

### JetDrawer
This takes in 3 collections of jets (ref jets, L1 jets, matched pairs) and plots them on a plot of eta Vs phi. It's handy for debugging and checking your matcher does something sensible. By default, RunMatcher plots the first 10 events. (I also don't like the name - draw vs plot is confusing, but plot makes it sound like it's plotting distributions).


## Robin's notes

If you want to make by hand, instead of using SCRAM, do:
```
g++ -std=c++11 -o matcherTest matcherTest.cpp -I ../interface `root-config --cflags --glibs`
```