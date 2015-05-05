# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:36:02 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import timetocross_sessions
from activitytables import info_key
from datapath import lesionshamcache, fullcrossings_key

# Load data
days = 'session < 17'
selection = str.format('trial > 0 and {0}',days)
cr = pd.read_hdf(lesionshamcache,fullcrossings_key).query(selection)
info = pd.read_hdf(lesionshamcache,info_key).query(days)

# Plot data
timetocross_sessions(cr,info)
locs,labels = plt.xticks()
labels = [l.get_text() for l in labels]
labels[0] = 'h'
plt.xticks(locs,labels)
ymin,ymax = plt.ylim()
plt.vlines(6*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(13*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(16*3+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)
plt.show()

# Save plot