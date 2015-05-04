# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:21:43 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import activitysummary
from activitytables import info_key, rewards_key
from datapath import lesionshamcache, leftpokebouts_key, rightpokebouts_key
from datapath import visiblecrossings_key, crossings_key

# Load data
control = '(lesionleft + lesionright) == 0'
lesion = '(lesionleft + lesionright) > 0'
info = pd.read_hdf(lesionshamcache,info_key)
rr = pd.read_hdf(lesionshamcache,rewards_key)
lpoke = pd.read_hdf(lesionshamcache,leftpokebouts_key)
rpoke = pd.read_hdf(lesionshamcache,rightpokebouts_key)
cr = pd.read_hdf(lesionshamcache,crossings_key)
vcr = pd.read_hdf(lesionshamcache,visiblecrossings_key)
infostable = info.query('1 <= session < 5')
infomanip = info.query('6 <= session < 11')

# Plot data
f, ((sc,sl),(mc,ml)) = plt.subplots(2,2)
activitysummary(infostable.query(control),rr,lpoke,rpoke,vcr,cr,ax=sc)
activitysummary(infostable.query(lesion),rr,lpoke,rpoke,vcr,cr,ax=sl)
activitysummary(infomanip.query(control),rr,lpoke,rpoke,vcr,cr,ax=mc)
activitysummary(infomanip.query(lesion),rr,lpoke,rpoke,vcr,cr,ax=ml)
sc.set_title('stable (control)')
sl.set_title('stable (lesion)')
mc.set_title('manipulation (control)')
ml.set_title('manipulation (lesion)')
plt.show()

# Save plot