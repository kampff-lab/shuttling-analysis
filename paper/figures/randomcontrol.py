# -*- coding: utf-8 -*-
"""
Created on Mon May 04 16:34:44 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key

# Load data
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
randomstable = str.format('({0}) and stepstate3',random)
randomunstable = str.format('({0}) and not stepstate3',random)
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)

# Plot data
axes = scatterhistaxes()
axScatter,axHistx,axHisty = axes
posturehistogram(steps.query(randomstable),color='b',axes=axes)
posturehistogram(steps.query(randomunstable),color='r',axes=axes)
axScatter.legend(['stable', 'unstable'],loc=2)
ntrials = len(steps.query(randomstable)) + len(steps.query(randomunstable))
axHistx.set_title(str.format("n = {0} trials",ntrials))
plt.show()

# Save plot
