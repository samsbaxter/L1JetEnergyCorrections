#L1 Jet Energy Corrections/Calibrations (JEC)

__tl;dr__: The code in here calculates corrections for jets from the Level 1 trigger.

This applies to:

- Legay GCT
- Stage 1
- Stage 2

It is an attempt to unify previous fragments of code lying around, in a *generic* way. So if you arrive here and need to use a new matching method, or want to calibrate using a different scheme, you can do it easily without digging around (too much).

## Installation

First make sure you have a copy of CMSSW (I'm using CMSSW_7_2_0_pre7). Then in `CMSSW_X_Y_Z/src`:

```shell
git clone XXX
XXX
```

## Running

```
XXX
```

## Basic concept

The following is an outline of the method that is used to calibrate jet energies.

1. Run a config file over a sample, running the relevant L1 emulator and produce 2 sets of jets: **reference jets** (e.g. `ak5GenJet`s) and **L1 jets** (the ones you want to calibrate, e.g. `L1GctInternJet`s).
2. Convert these jet collections into consistent collections, containing the info we need to calibrate (say, 4-vectors).
3. Pass these 2 collections to a Matcher. This will match L1 jets to reference jets, and output pairs of matched jets.
4. Pass matched pairs to a Calibration Calculator. This will calcualte the calibration constants, and produce plots.

## Derivations/Specialisation

The objects mentioned above (Matcher, Calibration calculator) are all **interfaces** (i.e abstract classes). Subclasses/derived classes of these actually perform the matching or calibrating *for some particular matching/calibration scheme*. This way, there is a unified interface, so one can easily swap in a different way of matching or calibrating without a) worrying that they're replacing the right parts/missing bits and b) mucking up some other bit of code.

It's trying to avoid some 1000 line ROOT script where all the important procedures are hidden away, and are coupled to some particular setup.

The top-level script is XXX. It instigates a Matcher and Calibration calculator. All you have to do is tell it which Matcher you want, and which Calibration calculator you want (plus a bit more info).

## An example

One type of jet matching is by deltaR(ref jet - L1 jet), where deltaR^2 = deltaEta^2 + deltaPhi^2 (all deltas are between ref and L1 jets). This is implemented in XXX.

One type of calibration scheme is by plotting the ratio of E_T for matched reference and L1 jets, and fitting with a particular function. This is shown in XXX.


## What if I want to do X?

- **I want to**
- **I want to**

## Robin's notes

