# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 15:32:27 2013

@author: gonca_000
"""

import os
import glob
import poke
import numpy as np
        
def genfromtxt(path):
    leftpokepath = os.path.join(path, 'left_poke.csv')
    leftrewardpath = os.path.join(path, 'left_rewards.csv')
    leftpoke = poke.genfromtxt(leftpokepath, leftrewardpath)
    
    rightpokepath = os.path.join(path, 'right_poke.csv')
    rightrewardpath = os.path.join(path, 'right_rewards.csv')
    rightpoke = poke.genfromtxt(rightpokepath, rightrewardpath)
    
    return shuttling(path, leftpoke, rightpoke, (leftpoke+rightpoke).rewards)
    
def findsessions(folder):
    sessionpaths = glob.glob(os.path.join(folder,'**/front_video.csv'))
    return [os.path.split(path)[0] for path in sessionpaths]