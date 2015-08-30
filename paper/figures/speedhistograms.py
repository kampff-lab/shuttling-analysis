# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 11:21:58 2015

@author: Gonçalo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from activitytables import flipleftwards, info_key
from shuttlingplots import speedhistogram, speedcorrelation, scatterhistaxes
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import names, control, lesion, smalllesion, anylesion

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
nonjumpers = str.format("subject not in {0}",jumpers)
sessions = str.format("{0} or {1}",stable,unstable)
info = pd.read_hdf(lesionshamcache, info_key)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smalllesions = str.format("subject in {0}",list(names(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
steps.xhead_speed[steps.side == 'leftwards'] *= -1
steps.xhead = flipleftwards(steps.xhead,steps.side)
steps = steps.query(sessions)

# Plot functions
rangex = (steps.xhead_speed.min(),steps.xhead_speed.max())
rangey = (steps.yhead_speed.min(),steps.yhead_speed.max())
def histogramcomparison(steps,title):
    axes = scatterhistaxes()
    axScatter,axHistx,axHisty = axes
    speedhistogram(steps.query(stable),rangex,rangey,color='b',axes=axes)
    speedhistogram(steps.query(unstable),rangex,rangey,color='r',axes=axes)
    axScatter.legend(['stable', 'unstable'],loc=2)
    ntrials = len(steps.query(stable)) + len(steps.query(unstable))
    axHistx.set_title(str.format("n = {0} trials",ntrials))
    plt.suptitle(title)
    
headrange = (steps.xhead.min()-1,steps.xhead.max()+1)
def speedcomparison(steps,title):
    fig = plt.figure()
    ax = fig.gca()
    speedcorrelation(steps.query(stable),rangex,headrange,'b',ax=ax)
    speedcorrelation(steps.query(unstable),rangex,headrange,'r',ax=ax)
    ax.legend(['stable', 'unstable'],loc=4)
    ntrials = len(steps.query(stable)) + len(steps.query(unstable))
    ax.set_title(str.format("n = {0} trials",ntrials))
    plt.suptitle(title)

# Plot data
histogramcomparison(steps,'all')
histogramcomparison(steps.query(lesions),'lesions')
histogramcomparison(steps.query(smalllesions),'small lesions')
histogramcomparison(steps.query(alllesions),'all lesions')
histogramcomparison(steps.query(controls),'controls')
speedcomparison(steps,'all')
speedcomparison(steps.query(lesions),'lesions')
speedcomparison(steps.query(smalllesions),'small lesions')
speedcomparison(steps.query(alllesions),'all lesions')
speedcomparison(steps.query(controls),'controls')
plt.show()

# Save plot
