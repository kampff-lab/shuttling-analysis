# -*- coding: utf-8 -*-
"""
Created on Sat May 02 15:06:05 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from shuttlingplots import averageposturecomparison, proxylegend
from datapath import lesionshamcache, crossings_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key
from infotables import lesionordermap

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
info = pd.read_hdf(lesionshamcache,info_key)
lesionmap = lesionordermap(info)
cr = pd.read_hdf(lesionshamcache,crossings_key).query('trial > 0')
scract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
ucract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
cract = pd.concat([scract,ucract])
cract.reset_index(['subject','session','crossing'],inplace=True)

# Plot data
def plotaverage(subject,ax):
    cr1 = cr.query(str.format("subject == '{0}' and {1}",subject,unstable))
    cr2 = cr.query(str.format("subject == '{0}' and {1}",subject,stable))
    averageposturecomparison(cract,info,cr1,cr2,ax=ax)
    ax.set_title(lesionmap[subject])

f, (ex1,ex2) = plt.subplots(1,2)
plotaverage('JPAK_21',ex1)
plotaverage('JPAK_24',ex2)
proxylegend(['g','r'],['stable','unstable'],ax=ex1,
            loc='lower left',bbox_to_anchor=(0.8,1))
plt.tight_layout()
plt.show()

# Save plot
