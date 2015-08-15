# -*- coding: utf-8 -*-
"""
Created on Mon May 04 19:31:59 2015

@author: Gonçalo
"""

from activitytables import rewards_key
from activitytables import read_subjects, pokebouts
from preprocess import leftpoke_key, rightpoke_key
from datapath import lesionsham, decorticate
from datapath import lesionshamcache, decorticatecache
from datapath import leftpokebouts_key, rightpokebouts_key

# Rebuild info cache
print "Rebuilding lesionsham poke info..."
rr = read_subjects(lesionsham,key=rewards_key)
lpoke = read_subjects(lesionsham,key=[leftpoke_key,rewards_key],
                      selector=pokebouts)
rpoke = read_subjects(lesionsham,key=[rightpoke_key,rewards_key],
                      selector=pokebouts)
rr.to_hdf(lesionshamcache,rewards_key)
lpoke.to_hdf(lesionshamcache,leftpokebouts_key)
rpoke.to_hdf(lesionshamcache,rightpokebouts_key)

print "Rebuilding decorticate poke info..."
rr = read_subjects(decorticate,key=rewards_key)
lpoke = read_subjects(decorticate,key=[leftpoke_key,rewards_key],
                      selector=pokebouts)
rpoke = read_subjects(decorticate,key=[rightpoke_key,rewards_key],
                      selector=pokebouts)
rr.to_hdf(decorticatecache,rewards_key)
lpoke.to_hdf(decorticatecache,leftpokebouts_key)
rpoke.to_hdf(decorticatecache,rightpokebouts_key)
