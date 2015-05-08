# -*- coding: utf-8 -*-
"""
Created on Wed May 06 15:30:18 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names
from activitytables import posturebias, getballistictrials, info_key
from shuttlingplots import averagetrajectory, proxylegend
from datapath import jumpers, lesionshamcache, crossings_key
from datapath import crossingactivity_random_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)

# Select data
bias = 2
group = list(names(info))
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
cr = cr.query(random)
for name in group:
    selection = str.format("subject in {0}",[name])
    try:
        scr = cr.query(selection)
        stablebias,unstablebias = posturebias(scr,n=bias)
        stablebias = getballistictrials(stablebias)
        unstablebias = getballistictrials(unstablebias)
    except Exception:
        continue
    
    # Plot data
    fig = plt.figure()
    ax = fig.gca()
    ss = stablebias.query('not stepstate3')
    us = unstablebias.query('not stepstate3')
    averagetrajectory(cract,ss,color='b',ax=ax)
    averagetrajectory(cract,us,color='r',ax=ax)
    proxylegend(['b','r'],['stable bias','unstable bias'],ax=ax)
    ax.set_title(str.format('{0} (n = {1} trials)',name,len(ss)+len(us)))
    #plt.title(str.format('stable (n = {0} trials)',len(cr.query(stable))))
plt.show()
    
# Save plot
