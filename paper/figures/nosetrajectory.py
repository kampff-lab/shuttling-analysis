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
from shuttlingplots import averagetrajectory, proxylegend
from datapath import lesionshamcache, crossings_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key
from datapath import crossingactivity_restable_key
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
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr).query(selected)

# Plot data
f, (sx,ux,rx) = plt.subplots(1,3)
cract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
averagetrajectory(cract,cr.query(stable).query(nonjumpers),color='b',ax=sx)
averagetrajectory(cract,cr.query(stable).query(jumpers),color='r',ax=sx)
proxylegend(['b','r'],['nonjumper','jumper'],ax=sx)
sx.set_title(str.format('stable (n = {0} trials)',len(cr.query(stable))))
sx.set_ylabel('y (cm)')
sx.set_ylim(0,6)

cract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
averagetrajectory(cract,cr.query(unstable).query(nonjumpers),color='b',ax=ux)
averagetrajectory(cract,cr.query(unstable).query(jumpers),color='r',ax=ux)
ux.set_title(str.format('unstable (n = {0} trials)',len(cr.query(unstable))))
ux.set_ylabel('y (cm)')
ux.set_ylim(0,6)

cract = pd.read_hdf(lesionshamcache,crossingactivity_restable_key)
averagetrajectory(cract,cr.query(restable).query(nonjumpers),color='b',ax=rx)
averagetrajectory(cract,cr.query(restable).query(jumpers),color='r',ax=rx)
rx.set_title(str.format('restable (n = {0} trials)',len(cr.query(restable))))
rx.set_ylabel('y (cm)')
rx.set_ylim(0,6)

plt.tight_layout(w_pad=1)
plt.show()

# Save plot
