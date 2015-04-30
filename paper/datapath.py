# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:20:49 2015

@author: Gonçalo
"""

import os

_lesionshampath_ = r'D:/Protocols/Shuttling/LightDarkServoStable'
_decorticatepath_ = r'D:/Protocols/Shuttling/Decorticate'

lesionshamdata = os.path.join(_lesionshampath_,'Data')
lesionshamanalysis = os.path.join(_lesionshampath_,'Analysis')
decorticatedata = os.path.join(_decorticatepath_,'Data')
decorticateanalysis = os.path.join(_decorticatepath_,'Analysis')

lesionshamcache = os.path.join(lesionshamanalysis,'cache.hdf5')
decorticatecache = os.path.join(decorticateanalysis,'cache.hdf5')
visiblecrossings_key = 'visiblecrossings'
fullcrossings_key = 'fullcrossings'
crossings_key = 'crossings'

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
