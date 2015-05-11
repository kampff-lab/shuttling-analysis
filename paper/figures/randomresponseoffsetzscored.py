# -*- coding: utf-8 -*-
"""
Created on Sat May 09 17:39:02 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names, cagemates, control, lesion, smalllesion
from activitytables import info_key, getballistictrials
from activitytables import crossingoffset, joinstepactivity, normalizeposition
from shuttlingplots import groupcomparison, proxylegend
from datapath import jumpers, lesionshamcache, stepfeatures_key
from datapath import crossingactivity_random_key, crossings_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
cr = pd.read_hdf(lesionshamcache,crossings_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
cract.reset_index(['subject','session','crossing'],inplace=True)
info = pd.read_hdf(lesionshamcache, info_key).query(nonjumpers)
info = info.query("subject != 'JPAK_20'")

# Select data
group = list(names(info))
controls = list(names(control(info)))
lesions = list(names(lesion(info)))
matched = list(cagemates(lesion(info)))
small = list(names(smalllesion(info)))
selection = str.format("subject in {0}",group)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = steps.query(random).query(selection)
cr = cr.query(random).query(selection)
steps = joinstepactivity(steps,cr,cract)
steps = getballistictrials(steps)

for i in range(1,22):
    offact = crossingoffset(cract,steps,i)
    offact.set_index(['subject','session'],inplace=True)
    normalizeposition(offact,inplace=True)
    
    fig = plt.figure()
    ax = fig.gca()
    conditions = [offact.query('stepstate3'),
                  offact.query('not stepstate3')]
    groupcomparison('yhead',
                    [controls,small,lesions,matched],
                    conditions,colors=['b','r'],
                    ax=ax)
    proxylegend(['b','r'],['stable','unstable'])
    ax.set_xticklabels(['controls',
                        'small\nlesions',
                        'lesions',
                        'matched\ncontrols'])
    ax.set_title(str.format('nose height {0} cm after crossing step',i))
    ax.set_ylim(-1,1)
plt.show()
    
# Save plot
