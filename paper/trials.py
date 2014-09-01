# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 18:12:21 2014

@author: Gonçalo
"""

import os
import itertools
import numpy as np

def gettrialindices(path):
    leftrewardspath = os.path.join(path, 'left_rewards.csv')
    rightrewardspath = os.path.join(path, 'right_rewards.csv')
    frametimespath = os.path.join(path, 'front_video.csv')
    leftrewards = np.genfromtxt(leftrewardspath,dtype=str)
    rightrewards = np.genfromtxt(rightrewardspath,dtype=str)
    frametimes = np.genfromtxt(frametimespath,dtype=str)
    rewards = (r for sl in (t for t in itertools.izip_longest(leftrewards,rightrewards)) for r in sl)

    trial = 0
    trials = []
    target = next(rewards, None)
    for time in frametimes:
        if (target != None) and time > target:
            trial = trial + 1
            target = next(rewards, None)
        trials.append(trial)
    return np.array(trials)
    
def gettrialstate(stepstatepath,trials):
    stepstate = np.genfromtxt(stepstatepath,dtype=bool)
    return np.array([stepstate[t] for t in trials])