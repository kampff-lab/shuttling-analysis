# -*- coding: utf-8 -*-
"""
Created on Mon May 04 16:34:44 2015

@author: Gonçalo
"""

import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from activitytables import normalize, mediannorm, flipleftwards, info_key
from shuttlingplots import posturehistogram, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import control, lesion, smalllesion, anylesion
from infotables import names, cagemates, lesionordermap

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
info = pd.read_hdf(lesionshamcache, info_key)
lesionmap = lesionordermap(info)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smallnames = names(smalllesion(info))
smalllesions = str.format("subject in {0}",list(smallnames))
smalllesion_A = str.format("subject in ['{0}']",smallnames[0])
smalllesion_B = str.format("subject in ['{0}']",smallnames[1])
smallcontrols = str.format("subject in {0}",list(cagemates(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))

# Select data
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
randomstable = str.format('({0}) and stepstate3',random)
randomunstable = str.format('({0}) and not stepstate3',random)
steps = steps.query(random)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])

# Plot functions
rangex = (steps.xhead.min(),steps.xhead.max())
rangey = (steps.yhead.min(),steps.yhead.max())
def histogramcomparison(steps,title):
    axes = scatterhistaxes()
    axScatter,axHistx,axHisty = axes
    stepstable = steps.query(randomstable)
    stepunstable = steps.query(randomunstable)
    posturehistogram(stepstable,rangex,rangey,color='b',axes=axes)
    posturehistogram(stepunstable,rangex,rangey,color='r',axes=axes)
    axScatter.legend(['stable', 'unstable'],loc=2)
    t,p = stats.ttest_ind(stepstable.xhead,stepunstable.xhead)
    ntrials = len(stepstable) + len(stepunstable)
    axHistx.set_title(str.format("n = {0} trials (p = {1:.5f})",ntrials,p))
    plt.suptitle(title)
    
# Plot data
histogramcomparison(steps,'all')
histogramcomparison(steps.query(lesions),'lesions')
histogramcomparison(steps.query(smalllesions),'small lesions')
histogramcomparison(steps.query(smalllesion_A),lesionmap[smallnames[0]])
histogramcomparison(steps.query(smalllesion_B),lesionmap[smallnames[1]])
histogramcomparison(steps.query(smallcontrols),'small controls')
histogramcomparison(steps.query(alllesions),'all lesions')
histogramcomparison(steps.query(controls),'controls')
plt.show()

# Save plot
