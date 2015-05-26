# -*- coding: utf-8 -*-
"""
Created on Tue May 26 15:54:24 2015

@author: Gonçalo
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 02 00:15:35 2015

@author: Gonçalo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from activitytables import getballistictrials
from infotables import control, anylesion
from shuttlingplots import skipprobability, proxylegend
from datapath import lesionshamcache, crossings_key
from datapath import jumpers

# Load data
unstable = '(9 <= session < 11)'
removed = "subject not in ['JPAK_20']"
selected = str.format("{0} and {1} and trial > 0",unstable,removed)
nonjumpers = str.format("subject not in {0}",jumpers)
jumpers = str.format("subject in {0}",jumpers)
info = pd.read_hdf(lesionshamcache,info_key)
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Select data
cr = cr.query(selected).join(info)
cr.protocol[cr.eval(unstable)] = 'unstable'
sp = skipprobability(cr)
sinfo = info.query('session == 0').reset_index('session')
sp.reset_index('protocol',drop=True,inplace=True)
sp = sp.join(sinfo)
sp.age /= np.timedelta64(1,'D')

# Plot data
f, ax = plt.subplots(1,1)
control(sp).plot(x='weight',y='frequency',color='b',
                 kind='scatter',grid=False,ax=ax)
anylesion(sp).plot(x='weight',y='frequency',color='r',
                   kind='scatter',grid=False,ax=ax)
ax.set_xlabel('weight (g)')
ax.set_ylabel('p (skip middle steps)')
ax.set_title('correlation of jumping with weight')
proxylegend(['b','r'],['control','lesion'])
plt.show()

# Save plot
