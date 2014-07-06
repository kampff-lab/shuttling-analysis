# -*- coding: utf-8 -*-
"""
Created on Sun Jun 09 20:37:46 2013

@author: gonca_000
"""

import ast
import glob
import numpy as np

def load_stepactivity(path):
    activities = []
    with open(path) as f:
        for line in f:
            activities.append(np.array(ast.literal_eval(line)))
    return activities

def load_stepactivities(datafolder):
    return [load_stepactivity(path) for path in glob.glob(datafolder + '/*/*/*trajectory_steps.csv')]
    
def threshold_steps(steps,lowT,highT):
    result = np.zeros(steps.shape,dtype=bool)
    for i in range(steps.shape[0]):
        for j in range(steps.shape[1]):
            if steps[i,j] > highT:
                result[i,j] = True
            else:
                if steps[i,j] < lowT or i == 0:
                    result[i,j] = False
                else:
                    result[i,j] = result[i-1,j]
    return result
    
def get_first_step_onsets(steps,stepindex,lowT=50000,highT=75000):
    onsets = []
    for s in steps:
        step_onsets = get_step_onsets(s,lowT,highT)
        first_onset = np.nonzero(step_onsets[1] == stepindex)[0]
        if len(first_onset) > 0:
            onsets.append(step_onsets[0][first_onset[0]])
        else:
            onsets.append(None)
    return onsets
    
def get_step_onsets(steps,lowT=50000,highT=75000):
    stepthreshold = threshold_steps(steps,lowT,highT).astype(int)
    return np.nonzero(np.diff(stepthreshold,axis=0) > 0)