# -*- coding: utf-8 -*-
"""
Created on Mon May 04 17:11:32 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 10, 5

import infotables
import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from shuttlingplots import posturehistogram
from datapath import jumpers
from datapath import lesionshamcache, stepfeatures_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)
lesioninfo = infotables.lesion(info)
lesion = str.format("subject in {0}",list(infotables.names(lesioninfo)))
control = str.format("subject in {0}",list(infotables.cagemates(lesioninfo)))
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
scract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
ucract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
cract = pd.concat([scract,ucract])
cract.reset_index(['subject','session','crossing'],inplace=True)

# Plot data
plt.figure()
axScatter = plt.subplot2grid((3,7),(1,0),rowspan=2,colspan=2)
axHistx = plt.subplot2grid((3,7),(0,0),colspan=2)
axHisty = plt.subplot2grid((3,7),(1,2),rowspan=2)
axes = (axScatter,axHistx,axHisty)
ssteps = steps.query(stable)
posturehistogram(ssteps.query(control),color='b',axes=axes)
posturehistogram(ssteps.query(lesion),color='r',axes=axes)
axScatter.legend(['control', 'lesion'],loc=2)
ntrials = len(ssteps.query(control)) + len(ssteps.query(lesion))
axHistx.set_title(str.format("n = {0} trials (stable)",ntrials))

axScatter = plt.subplot2grid((3,7),(1,4),rowspan=2,colspan=2)
axHistx = plt.subplot2grid((3,7),(0,4),colspan=2)
axHisty = plt.subplot2grid((3,7),(1,6),rowspan=2)
axes = (axScatter,axHistx,axHisty)
usteps = steps.query(unstable)
posturehistogram(usteps.query(control),color='b',axes=axes)
posturehistogram(usteps.query(lesion),color='r',axes=axes)
axScatter.legend(['control', 'lesion'],loc=2)
ntrials = len(usteps.query(control)) + len(usteps.query(lesion))
axHistx.set_title(str.format("n = {0} trials (unstable)",ntrials))
plt.show()

# Save plot
