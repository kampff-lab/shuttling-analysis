# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\IntelligentSystems\.spyder2\.temp.py
"""

import os
import numpy as np
import matplotlib as mpl

proceed = True
filename = 'crossings.csv'
timestamp_filename = '../front_video.csv'
activity_filename = '../center_activity.csv'
if os.path.exists(filename):
    ans = raw_input('File exists - overwrite? (y/n)')
    if ans != 'y':
        proceed = False

if proceed:    
    timestamps = np.genfromtxt(timestamp_filename,usecols=0,dtype=str)
    if os.path.exists(activity_filename):
        area = np.genfromtxt(activity_filename)
    else:
        area = np.genfromtxt(timestamp_filename,usecols=4)
    
    crosses = np.insert(np.diff(np.array(area > 500000,dtype=int)),0,0)
    cross_in = mpl.mlab.find(crosses > 0)
    cross_out = mpl.mlab.find(crosses < 0)
    ici = cross_in[1:] - cross_out[0:len(cross_out)-1]
    valid_crosses = np.insert(ici > 120,0,True)
    cross_times = timestamps[cross_in[valid_crosses]]
    np.savetxt(filename,cross_times,'%s')