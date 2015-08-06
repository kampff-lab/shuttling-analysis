# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:20:49 2015

@author: Gonçalo
"""

import os
import pandas as pd

_lesionshampath_ = r'D:/Protocols/Shuttling/LightDarkServoStable'
_decorticatepath_ = r'D:/Protocols/Shuttling/Decorticate'

lesionshamdata = os.path.join(_lesionshampath_,'Data')
lesionshamanalysis = os.path.join(_lesionshampath_,'Analysis')
decorticatedata = os.path.join(_decorticatepath_,'Data')
decorticateanalysis = os.path.join(_decorticatepath_,'Analysis')

lesionshamcache = os.path.join(lesionshamanalysis,'cache.hdf5')
decorticatecache = os.path.join(decorticateanalysis,'cache.hdf5')
crossingactivity_stable_key = 'crossingactivity_stable'
crossingactivity_unstable_key = 'crossingactivity_unstable'
crossingactivity_restable_key = 'crossingactivity_restable'
crossingactivity_random_key = 'crossingactivity_random'
crossingactivity_challenge_key = 'crossingactivity_challenge'
visiblecrossings_key = 'visiblecrossings'
fullcrossings_key = 'fullcrossings'
crossings_key = 'crossings'
stepfeatures_key = 'stepfeatures'
leftpokebouts_key = 'task/poke/left/pokebouts'
rightpokebouts_key = 'task/poke/right/pokebouts'

lesionsham = [os.path.join(lesionshamdata,'JPAK_20'),
              os.path.join(lesionshamdata,'JPAK_21'),
              os.path.join(lesionshamdata,'JPAK_22'),
              os.path.join(lesionshamdata,'JPAK_23'),
              os.path.join(lesionshamdata,'JPAK_24'),
              os.path.join(lesionshamdata,'JPAK_25'),
              os.path.join(lesionshamdata,'JPAK_26'),
              os.path.join(lesionshamdata,'JPAK_27'),
              os.path.join(lesionshamdata,'JPAK_28'),
              os.path.join(lesionshamdata,'JPAK_29'),
              os.path.join(lesionshamdata,'JPAK_36'),
              os.path.join(lesionshamdata,'JPAK_37'),
              os.path.join(lesionshamdata,'JPAK_38'),
              os.path.join(lesionshamdata,'JPAK_39'),
              os.path.join(lesionshamdata,'JPAK_48'),
              os.path.join(lesionshamdata,'JPAK_49'),
              os.path.join(lesionshamdata,'JPAK_50'),
              os.path.join(lesionshamdata,'JPAK_51'),
              os.path.join(lesionshamdata,'JPAK_52'),
              os.path.join(lesionshamdata,'JPAK_53'),
              os.path.join(lesionshamdata,'JPAK_54'),
              os.path.join(lesionshamdata,'JPAK_55')]
            
decorticate = [os.path.join(decorticatedata,'JPAK_79'),
               os.path.join(decorticatedata,'JPAK_81'),
               os.path.join(decorticatedata,'JPAK_82')]
               
jumpers = ['JPAK_38'] + [str.format('JPAK_{0}',i) for i in range(48,56)]
               
def _findsubjectpath_(name,subjects):
    result = filter(lambda x: os.path.split(x)[1] == name,subjects)
    if len(result) > 0:
        return result[0]
    else:
        return None
               
def subjectpath(name):
    result = _findsubjectpath_(name,lesionsham)
    if result != None:
        return result
    else:
        return _findsubjectpath_(name,decorticate)

def relativepath(info,path):
    return os.path.join(subjectpath(info.name[0]),info.dirname,path)

def sessionpath(info,path=''):
    return pd.Series(info.reset_index().apply(
        lambda x:os.path.join(subjectpath(x.subject), x.dirname, path),
        axis=1).values,
        index = info.index,
        name='path')