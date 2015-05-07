# -*- coding: utf-8 -*-
"""
Created on Mon May 04 17:11:32 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 10, 5

import infotables
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from activitytables import info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import posturehistogram
from datapath import jumpers
from datapath import lesionshamcache, stepfeatures_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
nonjumpers = str.format("subject not in {0}",jumpers)
sessions = str.format("{0} or {1}",stable,unstable)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)

# Select data
lesioninfo = infotables.lesion(info)
lesion = str.format("subject in {0}",list(infotables.names(lesioninfo)))
control = str.format("subject in {0}",list(infotables.cagemates(lesioninfo)))
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])
steps = steps.query(sessions)
stepstable = steps.query(stable)
stepunstable = steps.query(unstable)

# Plot data
plt.figure()
rangex = (steps.xhead.min(),steps.xhead.max())
rangey = (steps.yhead.min(),steps.yhead.max())
axScatter = plt.subplot2grid((3,7),(1,0),rowspan=2,colspan=2)
axHistx = plt.subplot2grid((3,7),(0,0),colspan=2)
axHisty = plt.subplot2grid((3,7),(1,2),rowspan=2)
axes = (axScatter,axHistx,axHisty)
scontrol = stepstable.query(control)
slesion = stepstable.query(lesion)
posturehistogram(scontrol,rangex,rangey,color='b',axes=axes)
posturehistogram(slesion,rangex,rangey,color='r',axes=axes)
axScatter.legend(['control', 'lesion'],loc=2)
t,p = stats.ttest_ind(scontrol.xhead,slesion.xhead)
ntrials = len(scontrol) + len(slesion)
axHistx.set_title(str.format("n = {0} trials (stable, p = {1:.5f})",ntrials,p))

axScatter = plt.subplot2grid((3,7),(1,4),rowspan=2,colspan=2)
axHistx = plt.subplot2grid((3,7),(0,4),colspan=2)
axHisty = plt.subplot2grid((3,7),(1,6),rowspan=2)
axes = (axScatter,axHistx,axHisty)
ucontrol = stepunstable.query(control)
ulesion = stepunstable.query(lesion)
posturehistogram(ucontrol,rangex,rangey,color='b',axes=axes)
posturehistogram(ulesion,rangex,rangey,color='r',axes=axes)
axScatter.legend(['control', 'lesion'],loc=2)
t,p = stats.ttest_ind(ucontrol.xhead,ulesion.xhead)
ntrials = len(ucontrol) + len(ulesion)
axHistx.set_title(str.format("n = {0} trials (stable, p = {1:.5f})",ntrials,p))
plt.show()

# Save plot
