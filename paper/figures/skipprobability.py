# -*- coding: utf-8 -*-
"""
Created on Sat May 02 00:15:35 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

import pandas as pd
import matplotlib.pyplot as plt
from infotables import lesionvolume
from activitytables import info_key
from activitytables import getballistictrials
from shuttlingplots import skipprobability_subject
from datapath import lesionshamcache, crossings_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
restable = '(11 <= session < 13)'
removed = "subject not in ['JPAK_20']"
selected = str.format("({0} or {1} or {2}) and {3} and trial > 0",
                      stable,unstable,restable,removed)
info = pd.read_hdf(lesionshamcache,info_key)
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Select data
info['lesionvolume'] = lesionvolume(info)
cr = cr.query(selected).join(info)
cr.protocol[cr.eval(stable)] = 'stable'
cr.protocol[cr.eval(unstable)] = 'unstable'
cr.protocol[cr.eval(restable)] = 'restable'

info = info.query('session == 0')
info.reset_index('session',drop=True,inplace=True)

# Plot data
f, (sx,ux,rx) = plt.subplots(1,3)
skipprobability_subject(cr.query(stable),info,ax=sx)
skipprobability_subject(cr.query(unstable),info,ax=ux)
skipprobability_subject(cr.query(restable),info,ax=rx)
sx.set_title('stable')
ux.set_title('unstable')
rx.set_title('restable')
plt.tight_layout(w_pad=1)
plt.show()

# Save plot
