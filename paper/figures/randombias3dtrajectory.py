# -*- coding: utf-8 -*-
"""
Created on Sat May 09 17:04:16 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names,control,lesion,lesionordermap
from activitytables import posturebias, getballistictrials, info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import averagetimetrajectory, proxylegend
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
    
    # Select data
    stablebias = stablebias.rename(columns={'index':'crossing'})
    unstablebias = unstablebias.rename(columns={'index':'crossing'})
    stablebias.set_index('crossing',append=True,inplace=True)
    unstablebias.set_index('crossing',append=True,inplace=True)
    scract = cract.join(stablebias,how='inner',rsuffix='R')
    ucract = cract.join(unstablebias,how='inner',rsuffix='R')
    scract.xhead = flipleftwards(scract.xhead,scract.side)
    ucract.xhead = flipleftwards(ucract.xhead,ucract.side)
    sb_S = scract.query('stepstate3')
    sb_U = scract.query('not stepstate3')
    ub_S = ucract.query('stepstate3')
    ub_U = ucract.query('not stepstate3')
    
    # Plot data    
    name = namemap[name]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    averagetimetrajectory(sb_S,color='b',ax=ax,alpha=0.5)
    averagetimetrajectory(sb_U,color='cyan',ax=ax,alpha=0.5)
    averagetimetrajectory(ub_S,color='orange',ax=ax,alpha=0.5)
    averagetimetrajectory(ub_U,color='r',ax=ax,alpha=0.5)
    proxylegend(['b','cyan','orange','r'],
                ['stable bias [stable]',
                 'stable bias [unstable]',
                 'unstable bias [stable]',
                 'unstable bias [unstable]'],
                ax=ax,loc='upper left')
#    ax.set_ylim(0,3.5)
    ax.set_title(str.format('{0} (n = {1} trials)',name,
                            len(stablebias)+len(unstablebias)))
    #plt.title(str.format('stable (n = {0} trials)',len(cr.query(stable))))
plt.show()
    
# Save plot
