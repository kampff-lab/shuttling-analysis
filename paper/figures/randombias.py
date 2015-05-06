# -*- coding: utf-8 -*-
"""
Created on Tue May 05 23:21:27 2015

@author: Gonçalo
"""

import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from infotables import names
from activitytables import posturebias, info_key
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key
from datapath import crossingactivity_random_key

# Load data
bias = 2
nonjumpers = str.format("subject not in {0}",jumpers)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cract.reset_index(['subject','session','crossing'],inplace=True)

info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)
group = list(names(info))
selection = str.format("subject in {0}",group)
sb,ub = posturebias(steps.query(random).query(selection),n=bias)

# Plot data
axes = scatterhistaxes()
axScatter,axHistx,axHisty = axes
posturehistogram(sb,color='b',axes=axes)
posturehistogram(ub,color='r',axes=axes)
axScatter.legend(['stable', 'unstable'],loc=2)
ntrials = len(sb) + len(ub)
t,p = stats.ttest_ind(sb.xhead,ub.xhead)
axHistx.set_title(str.format("bias = {2}, n = {0} trials (p = {1:.5f})",ntrials,p,bias))
plt.show()
    
# Save plot
