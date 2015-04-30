# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:22:33 2015

@author: Gonçalo
"""

import matplotlib.pyplot as plt
from datapath import lesionsham
from shuttlingplots import timetoreward
from activitytables import read_subjects
from activitytables import rewards_key, info_key

# Load data
days = range(1,17)
rr = read_subjects(lesionsham,days,key=rewards_key)
info = read_subjects(lesionsham,days,key=info_key)  

# Plot data
timetoreward(rr,info)
ymin,ymax = plt.ylim()
plt.vlines(5*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(12*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(15*3+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)
plt.show()

# Save plot