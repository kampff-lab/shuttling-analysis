# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 12:21:43 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import activitysummary
from activitytables import read_subjects, info_key
from datapath import lesionsham, lesionshamcache
from datapath import visiblecrossings_key, crossings_key

# Load data
stabledays = range(1,5)
manipdays = range(6,11)
control = '(lesionleft + lesionright) == 0'
lesion = '(lesionleft + lesionright) > 0'
infostable = read_subjects(lesionsham,stabledays,key=info_key)
infomanip = read_subjects(lesionsham,manipdays,key=info_key)
cr = pd.read_hdf(lesionshamcache,crossings_key)
vcr = pd.read_hdf(lesionshamcache,visiblecrossings_key)

# Plot data
f, ((sc,sl),(mc,ml)) = plt.subplots(2,2)
activitysummary(infostable.query(control),vcr_cache=vcr,cr_cache=cr,ax=sc)
activitysummary(infostable.query(lesion),vcr_cache=vcr,cr_cache=cr,ax=sl)
activitysummary(infomanip.query(control),vcr_cache=vcr,cr_cache=cr,ax=mc)
activitysummary(infomanip.query(lesion),vcr_cache=vcr,cr_cache=cr,ax=ml)
sc.set_title('stable (control)')
sl.set_title('stable (lesion)')
mc.set_title('manipulation (control)')
ml.set_title('manipulation (lesion)')
plt.show()

# Save plot