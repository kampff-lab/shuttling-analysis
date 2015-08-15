# -*- coding: utf-8 -*-
"""
Created on Sat May 02 22:09:50 2015

@author: Gonçalo
"""

from activitytables import read_subjects
from activitytables import info_key
from datapath import lesionsham, decorticate
from datapath import lesionshamcache, decorticatecache
from datapath import lesionshamanalysis, decorticateanalysis, ensurefolder

# Rebuild info cache
ensurefolder(lesionshamanalysis)
print "Rebuilding lesionsham session info..."
cr = read_subjects(lesionsham,key=info_key)
cr.to_hdf(lesionshamcache,info_key)

ensurefolder(decorticateanalysis)
print "Rebuilding decorticate session info..."
cr = read_subjects(decorticate,key=info_key)
cr.to_hdf(decorticatecache,info_key)