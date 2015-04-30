# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:13:54 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import timetocross_trials
from activitytables import read_subjects, info_key
from datapath import lesionsham, lesionshamcache, fullcrossings_key

# Load data
days = range(0,1)
selection = str.format('index < 5 and session < {0}',len(days))
cr = pd.read_hdf(lesionshamcache,fullcrossings_key).query(selection)
info = read_subjects(lesionsham,days,key=info_key)

# Plot data
timetocross_trials(cr,info)
plt.show()