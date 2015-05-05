# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:22:33 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from datapath import lesionshamcache
from shuttlingplots import timetoreward
from activitytables import rewards_key, info_key

# Load data
days = '1 <= session < 17'
rr = pd.read_hdf(lesionshamcache,rewards_key).query(days)
info = pd.read_hdf(lesionshamcache,info_key).query(days)

# Plot data
timetoreward(rr,info)
ymin,ymax = plt.ylim()
plt.vlines(5*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(12*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(15*3+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)
plt.show()

# Save plot