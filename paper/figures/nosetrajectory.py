# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 21:01:15 2015

@author: Gonçalo
"""

from pylab import rcParams
rcParams['figure.figsize'] = 15, 5

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import getballistictrials
from shuttlingplots import averagetrajectory
from datapath import lesionshamcache, crossings_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key
from datapath import crossingactivity_restable_key

# Load data
stable = '(1 <= session < 5) and trial > 0'
unstable = '(9 <= session < 11) and trial > 0'
restable = '(11 <= session < 13) and trial > 0'
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Plot data
f, (sx,ux,rx) = plt.subplots(1,3)
cract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
averagetrajectory(cract,cr.query(stable),ax=sx)
cract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
averagetrajectory(cract,cr.query(unstable),ax=ux)
cract = pd.read_hdf(lesionshamcache,crossingactivity_restable_key)
averagetrajectory(cract,cr.query(restable),ax=rx)
sx.set_title(str.format('stable (n = {0} trials)',len(cr.query(stable))))
ux.set_title(str.format('unstable (n = {0} trials)',len(cr.query(unstable))))
rx.set_title(str.format('restable (n = {0} trials)',len(cr.query(restable))))
plt.tight_layout(w_pad=1)
plt.show()

# Save plot
