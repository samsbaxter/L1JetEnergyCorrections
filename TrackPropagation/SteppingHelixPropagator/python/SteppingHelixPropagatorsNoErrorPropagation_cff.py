import FWCore.ParameterSet.Config as cms

#Just pick from other places and set to no error propagation
import TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi
SteppingHelixPropagatorAnyNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi.SteppingHelixPropagatorAny.clone()
SteppingHelixPropagatorAnyNoError.ComponentName = 'SteppingHelixPropagatorAnyNoError'
SteppingHelixPropagatorAnyNoError.NoErrorPropagation = True

import TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi
SteppingHelixPropagatorAlongNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi.SteppingHelixPropagatorAlong.clone()
SteppingHelixPropagatorAlongNoError.ComponentName = 'SteppingHelixPropagatorAlongNoError'
SteppingHelixPropagatorAlongNoError.NoErrorPropagation = True


import TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi
SteppingHelixPropagatorOppositeNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi.SteppingHelixPropagatorOpposite.clone()
SteppingHelixPropagatorOppositeNoError.ComponentName = 'SteppingHelixPropagatorOppositeNoError'
SteppingHelixPropagatorOppositeNoError.NoErrorPropagation = True

import TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorHLT_cff

SteppingHelixPropagatorL2AnyNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorHLT_cff.SteppingHelixPropagatorL2Any.clone()
SteppingHelixPropagatorL2AnyNoError.ComponentName = 'SteppingHelixPropagatorL2AnyNoError'
SteppingHelixPropagatorL2AnyNoError.NoErrorPropagation = True

SteppingHelixPropagatorL2AlongNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorHLT_cff.SteppingHelixPropagatorL2Along.clone()
SteppingHelixPropagatorL2AlongNoError.ComponentName = 'SteppingHelixPropagatorL2AlongNoError'
SteppingHelixPropagatorL2AlongNoError.NoErrorPropagation = True

SteppingHelixPropagatorL2OppositeNoError = TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorHLT_cff.SteppingHelixPropagatorL2Opposite.clone()
SteppingHelixPropagatorL2OppositeNoError.ComponentName = 'SteppingHelixPropagatorL2OppositeNoError'
SteppingHelixPropagatorL2OppositeNoError.NoErrorPropagation = True