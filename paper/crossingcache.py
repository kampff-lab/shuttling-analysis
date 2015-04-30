# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:30:38 2015

@author: Gonçalo
"""

from activitytables import read_subjects
from activitytables import visiblecrossings, fullcrossings, crossings
from datapath import lesionsham, decorticate
from datapath import lesionshamcache, decorticatecache
from datapath import visiblecrossings_key, fullcrossings_key, crossings_key

# Rebuild crossing cache
print "Rebuilding lesionsham visible crossings..."
cr = read_subjects(lesionsham,selector=visiblecrossings)
cr.to_hdf(lesionshamcache,visiblecrossings_key)

print "Rebuilding lesionsham full crossings..."
cr = read_subjects(lesionsham,selector=fullcrossings)
cr.to_hdf(lesionshamcache,fullcrossings_key)

print "Rebuilding lesionsham crossings..."
cr = read_subjects(lesionsham,selector=crossings)
cr.to_hdf(lesionshamcache,crossings_key)

print "Rebuilding decorticates visible crossings..."
cr = read_subjects(decorticate,selector=visiblecrossings)
cr.to_hdf(decorticatecache,visiblecrossings_key)

print "Rebuilding decorticates full crossings..."
cr = read_subjects(decorticate,selector=fullcrossings)
cr.to_hdf(decorticatecache,fullcrossings_key)

print "Rebuilding decorticates crossings..."
cr = read_subjects(decorticate,selector=crossings)
cr.to_hdf(decorticatecache,crossings_key)
