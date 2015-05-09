# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 23:03:25 2015

@author: Gonçalo
"""

from activitytables import read_subjects
from activitytables import crossingactivity
from datapath import lesionsham, decorticate
from datapath import lesionshamcache, decorticatecache
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key
from datapath import crossingactivity_restable_key
from datapath import crossingactivity_random_key
from datapath import crossingactivity_challenge_key

# Rebuild crossing trajectory cache
print "Rebuilding lesionsham stable trajectories..."
cr = read_subjects(lesionsham,days=slice(0,5),selector=crossingactivity)
cr.to_hdf(lesionshamcache,crossingactivity_stable_key)

print "Rebuilding lesionsham unstable trajectories..."
cr = read_subjects(lesionsham,days=slice(5,11),selector=crossingactivity)
cr.to_hdf(lesionshamcache,crossingactivity_unstable_key)

print "Rebuilding lesionsham restable trajectories..."
cr = read_subjects(lesionsham,days=slice(11,13),selector=crossingactivity)
cr.to_hdf(lesionshamcache,crossingactivity_restable_key)

print "Rebuilding lesionsham random trajectories..."
cr = read_subjects(lesionsham,days=slice(13,17),selector=crossingactivity)
cr.to_hdf(lesionshamcache,crossingactivity_random_key)

print "Rebuilding lesionsham challenge trajectories..."
cr = read_subjects(lesionsham,days=slice(17,None),selector=crossingactivity)
cr.to_hdf(lesionshamcache,crossingactivity_challenge_key)

print "Rebuilding decorticate stable trajectories..."
cr = read_subjects(decorticate,days=slice(0,5),selector=crossingactivity)
cr.to_hdf(decorticatecache,crossingactivity_stable_key)

print "Rebuilding decorticate unstable trajectories..."
cr = read_subjects(decorticate,days=5,selector=crossingactivity)
cr.to_hdf(decorticatecache,crossingactivity_unstable_key)

print "Rebuilding decorticate challenge trajectories..."
cr = read_subjects(decorticate,days=slice(6,None),selector=crossingactivity)
cr.to_hdf(decorticatecache,crossingactivity_challenge_key)