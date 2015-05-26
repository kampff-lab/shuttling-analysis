# -*- coding: utf-8 -*-
"""
Created on Sat May 02 00:15:35 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import lesionvolume
from activitytables import info_key
from activitytables import getballistictrials
from shuttlingplots import skipprobability, barcomparison, proxylegend
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
cr = pd.read_hdf(lesionshamcache,crossings_key)
cr = getballistictrials(cr)

# Select data
info['lesionvolume'] = lesionvolume(info)
cr = cr.query(selected).join(info)
cr.protocol[cr.eval(stable)] = 'stable'
cr.protocol[cr.eval(unstable)] = 'unstable'
cr.protocol[cr.eval(restable)] = 'restable'

# Plot data
sp = skipprobability(cr)
sp['category'] = None
sp.category[sp.eval(jumpers)] = 'jumper'
sp.category[sp.eval(nonjumpers)] = 'nonjumper'
sp.reset_index('subject',inplace=True)
f,ax = plt.subplots(1,1)
barcomparison(sp.query("protocol == 'stable'"),['b','r'],
              by='category',column='frequency',ax=ax)
barcomparison(sp.query("protocol == 'unstable'"),['b','r'],
              left=3,by='category',column='frequency',ax=ax)
barcomparison(sp.query("protocol == 'restable'"),['b','r'],
              left=6,by='category',column='frequency',ax=ax)
proxylegend(['b','r'],['nonjumpers','jumpers'])
ax.set_ylabel('p (skip middle steps)')
ax.set_xticks([0.9,3.9,6.9])
ax.set_xticklabels(['stable','unstable','restable'])
plt.show()

# Save plot
