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
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import names, control, lesion, smalllesion, anylesion

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smalllesions = str.format("subject in {0}",list(names(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))

# Select data
bias = 2
group = list(names(info))
selection = str.format("subject in {0}",group)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = steps.query(random).query(selection)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])

# Plot functions
rangex = (steps.xhead.min(),steps.xhead.max())
rangey = (steps.yhead.min(),steps.yhead.max())
def histogramcomparison(steps,title):
    axes = scatterhistaxes()
    axScatter,axHistx,axHisty = axes
    stablebias,unstablebias = posturebias(steps,n=bias)
    posturehistogram(stablebias,rangex,rangey,color='b',axes=axes)
    posturehistogram(unstablebias,rangex,rangey,color='r',axes=axes)
    axScatter.legend(['+bias', '-bias'],loc=2)
    ntrials = len(stablebias) + len(unstablebias)
    t,p = stats.ttest_ind(stablebias.xhead,unstablebias.xhead)
    axHistx.set_title(str.format("bias = {2}, n = {0} trials (p = {1:.5f})",
                      ntrials,p,bias))
    plt.suptitle(title)

# Plot data
histogramcomparison(steps,'all')
histogramcomparison(steps.query(lesions),'lesions')
histogramcomparison(steps.query(smalllesions),'small lesions')
histogramcomparison(steps.query(alllesions),'all lesions')
histogramcomparison(steps.query(controls),'controls')
plt.show()
    
# Save plot
