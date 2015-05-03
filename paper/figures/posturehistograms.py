# -*- coding: utf-8 -*-
"""
Created on Sun May 03 14:54:24 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
scract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
ucract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
cract = pd.concat([scract,ucract])
cract.reset_index(['subject','session','crossing'],inplace=True)

# Plot data
axes = scatterhistaxes()
axScatter,axHistx,axHisty = axes
posturehistogram(steps.query(stable),color='b',axes=axes)
posturehistogram(steps.query(unstable),color='r',axes=axes)
axScatter.legend(['stable', 'unstable'],loc=2)
ntrials = len(steps.query(stable)) + len(steps.query(unstable))
axHistx.set_title(str.format("n = {0} trials",ntrials))
plt.show()

# Save plot
