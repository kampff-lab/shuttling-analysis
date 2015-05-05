# -*- coding: utf-8 -*-
"""
Created on Sat May 02 10:25:23 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from activitytables import getballistictrials
from shuttlingplots import trajectorycluster
from datapath import lesionshamcache, crossings_key

# Load data
stable = '(1 <= session < 5) and trial > 0'
unstable = '(9 <= session < 11) and trial > 0'
restable = '(11 <= session < 13) and trial > 0'
info = pd.read_hdf(lesionshamcache,info_key).query('session == 0')
info.reset_index('session',drop=True,inplace=True)
lightweight = info.weight < 300
light = str.format("and subject in {0}", list(info[lightweight].index))
normal = str.format("and subject in {0}", list(info[~lightweight].index))
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Plot data
lightlabel = 'weight < 300'
normallabel = 'weight >= 300'
f, (sx,ux,rx) = plt.subplots(1,3)
trajectorycluster(cr.query(stable+normal),ax=sx,color='b',label=normallabel)
trajectorycluster(cr.query(stable+light),ax=sx,color='r',label=lightlabel)
trajectorycluster(cr.query(unstable+normal),ax=ux,color='b',label=normallabel)
trajectorycluster(cr.query(unstable+light),ax=ux,color='r',label=lightlabel)
trajectorycluster(cr.query(restable+normal),ax=rx,color='b',label=normallabel)
trajectorycluster(cr.query(restable+light),ax=rx,color='r',label=lightlabel)
sx.set_title('stable')
ux.set_title('unstable')
rx.set_title('restable')
plt.tight_layout(w_pad=1)
plt.show()

# Save plot
