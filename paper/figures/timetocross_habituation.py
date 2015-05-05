# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:13:54 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import timetocross_trials
from activitytables import info_key
from datapath import lesionshamcache, fullcrossings_key

# Load data
days = 'session == 0'
selection = str.format('index < 5 and {0}',days)
cr = pd.read_hdf(lesionshamcache,fullcrossings_key).query(selection)
info = pd.read_hdf(lesionshamcache,info_key).query(days)

# Plot data
timetocross_trials(cr,info)
plt.show()