# -*- coding: utf-8 -*-
"""
Created on Sun May 03 15:08:56 2015

@author: Gonçalo
"""

from activitytables import read_subjects
from activitytables import stepfeatures
from datapath import lesionsham, decorticate
from datapath import lesionshamcache, decorticatecache
from datapath import stepfeatures_key

# Rebuild crossing cache
print "Rebuilding lesionsham step features..."
cr = read_subjects(lesionsham,selector=stepfeatures)
cr.to_hdf(lesionshamcache,stepfeatures_key)

print "Rebuilding decorticate step features..."
cr = read_subjects(decorticate,selector=stepfeatures)
cr.to_hdf(decorticatecache,stepfeatures_key)
