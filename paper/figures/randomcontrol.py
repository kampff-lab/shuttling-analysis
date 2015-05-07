# -*- coding: utf-8 -*-
"""
Created on Mon May 04 16:34:44 2015

@author: Gonçalo
"""

import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)

# Select data
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
randomstable = str.format('({0}) and stepstate3',random)
randomunstable = str.format('({0}) and not stepstate3',random)
steps = steps.query(random)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])
stepstable = steps.query(randomstable)
stepunstable = steps.query(randomunstable)

# Plot data
axes = scatterhistaxes()
axScatter,axHistx,axHisty = axes
rangex = (steps.xhead.min(),steps.xhead.max())
rangey = (steps.yhead.min(),steps.yhead.max())
posturehistogram(stepstable,rangex,rangey,color='b',axes=axes)
posturehistogram(stepunstable,rangex,rangey,color='r',axes=axes)
axScatter.legend(['stable', 'unstable'],loc=2)
t,p = stats.ttest_ind(stepstable.xhead,stepunstable.xhead)
ntrials = len(stepstable) + len(stepunstable)
axHistx.set_title(str.format("n = {0} trials (p = {1:.5f})",ntrials,p))
plt.show()

# Save plot
