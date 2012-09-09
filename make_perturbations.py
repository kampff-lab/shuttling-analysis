# -*- coding: utf-8 -*-
"""
Created on Mon May 28 14:37:12 2012

@author: IntelligentSystems
"""

import numpy as np
from itertools import groupby

def make_perturbations(offset,num_trials,p,max_consecutive):
    num_perturbations = p * num_trials
    trials = np.zeros(num_trials-offset)
    trials[0:num_perturbations] = 1
    valid = False
    while not valid:
        np.random.shuffle(trials)
        consecutive = max([len(list(x)) for k,x in groupby(trials)])
        valid = consecutive <= max_consecutive
    trials = np.concatenate((np.zeros(offset), trials))
    return trials