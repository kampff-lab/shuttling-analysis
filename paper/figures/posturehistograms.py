# -*- coding: utf-8 -*-
"""
Created on Sun May 03 14:54:24 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import flipleftwards
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
nonjumpers = str.format("subject not in {0}",jumpers)
sessions = str.format("{0} or {1}",stable,unstable)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
steps.xhead = flipleftwards(steps.xhead,steps.side)
steps = steps.query(sessions)

# Plot data
axes = scatterhistaxes()
axScatter,axHistx,axHisty = axes
rangex = (steps.xhead.min(),steps.xhead.max())
rangey = (steps.yhead.min(),steps.yhead.max())
posturehistogram(steps.query(stable),rangex,rangey,color='b',axes=axes)
posturehistogram(steps.query(unstable),rangex,rangey,color='r',axes=axes)
axScatter.legend(['stable', 'unstable'],loc=2)
ntrials = len(steps.query(stable)) + len(steps.query(unstable))
axHistx.set_title(str.format("n = {0} trials",ntrials))
plt.show()

# Save plot
