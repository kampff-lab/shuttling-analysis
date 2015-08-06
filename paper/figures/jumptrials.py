# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 10:27:52 2015

@author: Gonçalo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from infotables import lesionvolume, names
from infotables import lesionordermap
from activitytables import info_key
from activitytables import getballistictrials
from shuttlingplots import skipmeasure, barcomparison, groupcomparison, proxylegend
from datapath import lesionshamcache, crossings_key
from datapath import jumpers

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
restable = '(11 <= session < 13)'
removed = "subject not in ['JPAK_20']"
selected = str.format("({0} or {1} or {2}) and {3} and trial > 0",
                      stable,unstable,restable,removed)
nonjumpers = str.format("subject not in {0}",jumpers)
jumpers = str.format("subject in {0}",jumpers)
info = pd.read_hdf(lesionshamcache,info_key)
namemap = lesionordermap(info)
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Select data
column = 'entryspeed'
info['lesionvolume'] = lesionvolume(info)
cr = cr.query(selected).join(info)
cr.protocol[cr.eval(stable)] = 'stable'
cr.protocol[cr.eval(unstable)] = 'unstable'
cr.protocol[cr.eval(restable)] = 'restable'
sm = skipmeasure(cr,column)

# Custom-sort by protocol
protocolorder = {'stable':0,'unstable':1,'restable':2}
sm['rank'] = sm['protocol'].map(protocolorder)
sm.sort(columns='rank',inplace=True)
sm.drop(labels='rank',axis=1)
sm = sm.groupby(['subject','protocol','skip'],sort=True)[column]
ms = [d for g,d in sm]

# Plot data
f,ax = plt.subplots(1,1)
groupcomparison(ms,
                ['b','b','g','g','r','r']*100,
                ['o','x','o','x','o','x']*100,
                ['b','none','g','none','r','none']*100,
                s=10,
                ax=ax)
proxylegend(['b','g','r'],['stable','restable','unstable'],loc='upper left')
ax.set_xticks(np.arange(2.5,len(ms)+2.5,6))
ax.set_xticklabels([namemap[name] for name in names(info)[1:]])
plt.ylabel('mean speed (cm/s)')
plt.title('average speed on entry (1st third of assay)')
plt.show()

# Save plot
