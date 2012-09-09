# -*- coding: utf-8 -*-
"""
Created on Mon Jun 04 20:18:27 2012

@author: IntelligentSystems
"""

import numpy as np

def make_step_times(session):
    for i in range(len(session.steps)):
        step_timestamps = flatten(step_times(session,i))
        np.savetxt('step%s_times.csv' % (i),step_timestamps,'%s')