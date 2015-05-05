# -*- coding: utf-8 -*-
"""
Created on Sat May 02 00:15:35 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from activitytables import getballistictrials
from shuttlingplots import skipprobability
from datapath import lesionshamcache, crossings_key

# Load data
stable = '(1 <= session < 5) and trial > 0'
unstable = '(9 <= session < 11) and trial > 0'
restable = '(11 <= session < 13) and trial > 0'
info = pd.read_hdf(lesionshamcache,info_key).query('session == 0')
info.reset_index('session',drop=True,inplace=True)
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Plot data
f, (sx,ux,rx) = plt.subplots(1,3)
skipprobability(cr.query(stable),info,ax=sx)
skipprobability(cr.query(unstable),info,ax=ux)
skipprobability(cr.query(restable),info,ax=rx)
sx.set_title('stable')
ux.set_title('unstable')
rx.set_title('restable')
plt.tight_layout(w_pad=1)
plt.show()

# Save plot
