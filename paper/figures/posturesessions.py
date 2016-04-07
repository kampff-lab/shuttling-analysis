# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 03:07:49 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import flipleftwards, info_key
from shuttlingplots import posturesessioncomparison
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import names, control, lesion, smalllesion, anylesion
from infotables import lesionordermap

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key)
lesionmap = lesionordermap(info)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smalllesions = str.format("subject in {0}",list(names(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
steps.xhead = flipleftwards(steps.xhead,steps.side)

# Plot data
steps = steps.query("subject != 'JPAK_20' and session < 17")
def posturecomparison(steps,title=None):
    fig = plt.figure()
    ax = fig.gca()
    posturesessioncomparison(steps,ax=ax)
    if title is not None:
        plt.suptitle(title)
posturecomparison(steps)
posturecomparison(steps,'all')
posturecomparison(steps.query(controls),'controls')
posturecomparison(steps.query(lesions),'lesions')
posturecomparison(steps.query(smalllesions),'small lesions')
plt.show()

# Save plot
