# -*- coding: utf-8 -*-
"""
Created on Fri May 08 00:36:22 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names,control,lesion,lesionordermap
from activitytables import posturebias, getballistictrials, info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import averagetimeseries, proxylegend
from datapath import jumpers, lesionshamcache, crossings_key
from datapath import crossingactivity_random_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key)
namemap = lesionordermap(info)
info = info.query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)
cract.reset_index('time',inplace=True)

# Select data
bias = 2
group = list(names(info))
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
cr = cr.query(random)
for name in group:
    selection = str.format("subject in {0}",[name])
    scr = cr.query(selection)
    stablebias,unstablebias = posturebias(scr,n=bias)
    stablebias = getballistictrials(stablebias)
    unstablebias = getballistictrials(unstablebias)
    if len(stablebias) == 0 or len(unstablebias) == 0:
        continue
    
    # Plot data
    name = namemap[name]
    fig = plt.figure()
    ax = fig.gca()
    ss = stablebias.rename(columns={'index':'crossing'}).query('not stepstate3')
    us = unstablebias.rename(columns={'index':'crossing'}).query('not stepstate3')
    ss.set_index('crossing',append=True,inplace=True)
    us.set_index('crossing',append=True,inplace=True)
    scract = cract.join(ss,how='inner',rsuffix='R')
    ucract = cract.join(us,how='inner',rsuffix='R')
    scract.xhead = flipleftwards(scract.xhead,scract.side)
    ucract.xhead = flipleftwards(ucract.xhead,ucract.side)
    averagetimeseries(scract,'xhead',color='b',ax=ax)
    averagetimeseries(ucract,'xhead',color='r',ax=ax)
    ax.set_ylabel('x (cm)')
    ax.set_xlim(0,3)
    proxylegend(['b','r'],['stable bias','unstable bias'],ax=ax)
    ax.set_title(str.format('{0} (n = {1} trials)',name,len(ss)+len(us)))
    #plt.title(str.format('stable (n = {0} trials)',len(cr.query(stable))))
plt.show()
    
# Save plot
