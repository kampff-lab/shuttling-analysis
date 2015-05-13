# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:20:47 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 12, 5

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names,control,lesion,cagemates,lesionordermap
from activitytables import joinstepactivity, getballistictrials, info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import averagetimeseries, proxylegend
from datapath import jumpers, lesionshamcache, crossings_key
from datapath import crossingactivity_random_key, stepfeatures_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cract.reset_index(['subject','session','crossing'],inplace=True)
info = pd.read_hdf(lesionshamcache, info_key)
namemap = lesionordermap(info)
info = info.query(nonjumpers)
info = info.query("subject != 'JPAK_20'")

# Select data
group = list(names(info))
controls = list(names(control(info)))
lesions = list(names(lesion(info)))
matched = list(cagemates(lesion(info)))
selection = str.format("subject in {0}",group)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = steps.query(random).query(selection)
cr = cr.query(random).query(selection)
steps = joinstepactivity(steps,cr,cract)
steps = getballistictrials(steps)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])
steps_S = steps.query('xhead >= 0').rename(columns={'index':'time'})
steps_U = steps.query('xhead < 0').rename(columns={'index':'time'})
cract.reset_index(inplace=True)
cract.set_index(['subject','session','crossing'],inplace=True)

# Select data
for name in group:
    selection = str.format("subject in {0}",[name])
    stablebias = steps_S.query(selection)
    unstablebias = steps_U.query(selection)
    if len(stablebias) == 0 or len(unstablebias) == 0:
        continue
    
    # Select data
    scract = cract.join(stablebias,how='inner',rsuffix='R')
    ucract = cract.join(unstablebias,how='inner',rsuffix='R')
    scract.xhead = flipleftwards(scract.xhead,scract.side)
    ucract.xhead = flipleftwards(ucract.xhead,ucract.side)    
    scract.xhead_speed[scract.side == 'leftwards'] *= -1
    ucract.xhead_speed[ucract.side == 'leftwards'] *= -1
    sb_S = scract.query('stepstate3')
    sb_U = scract.query('not stepstate3')
    ub_S = ucract.query('stepstate3')
    ub_U = ucract.query('not stepstate3')
    
    # Plot data
    alpha = 0.25
    name = namemap[name]
    baseline = slice(0,28)
    fig,(ax1,ax2) = plt.subplots(1,2)
    averagetimeseries(pd.concat([sb_S,ub_S]),baseline,'xhead_speed',
                      ax=ax1,color='b',alpha=alpha)
    averagetimeseries(pd.concat([sb_U,ub_U]),baseline,'xhead_speed',
                      ax=ax1,color='r',alpha=alpha)
    proxylegend(['b','r'],['stable','unstable'],ax=ax1,loc='upper left')    
    ax1.set_title('average speed across space')
    ax1.set_ylabel('speed (cm/s)')
    ax1.set_ylim(-20,30)
    
    averagetimeseries(sb_S,baseline,'xhead_speed',
                      ax=ax2,color='b',alpha=alpha)
    averagetimeseries(ub_S,baseline,'xhead_speed',
                      ax=ax2,color='orange',alpha=alpha)
    averagetimeseries(sb_U,baseline,'xhead_speed',
                      ax=ax2,color='cyan',alpha=alpha)
    averagetimeseries(ub_U,baseline,'xhead_speed',
                      ax=ax2,color='r',alpha=alpha)
    ax2.set_title('average speed across space')
    ax2.set_ylabel('speed (cm/s)')
    ax2.set_ylim(-20,30)
    proxylegend(['b','orange','cyan','r'],
                ['stable [+b]',
                 'stable [-b]',
                 'unstable [+b]',
                 'unstable [-b]'],
                ax=ax2,loc='upper left')
    fig.suptitle(str.format('{0} (n = {1} trials)',name,
                            len(stablebias)+len(unstablebias)))
plt.show()

# Save plot
