# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\IntelligentSystems\.spyder2\.temp.py
"""

import os
from numpy import *

proceed = True
filename = 'crossings.csv'
if os.path.exists(filename):
    ans = raw_input('File exists - overwrite? (y/n)')
    if ans != 'y':
        proceed = False

if proceed:    
    timestamps = genfromtxt('../front_video.csv',usecols=0,dtype=str)
    area = genfromtxt('../front_video.csv',usecols=4)
    crosses = insert(diff(array(area > 3000,dtype=int)),0,0)
    cross_in = find(crosses > 0)
    cross_out = find(crosses < 0)
    ici = cross_in[1:] - cross_out[0:len(cross_out)-1]
    valid_crosses = insert(ici > 120,0,True)
    cross_times = timestamps[cross_in[valid_crosses]]
    savetxt(filename,cross_times,'%s')