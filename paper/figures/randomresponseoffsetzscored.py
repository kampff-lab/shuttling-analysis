# -*- coding: utf-8 -*-
"""
Created on Sat May 09 17:39:02 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from infotables import names, cagemates, control, lesion, smalllesion
from activitytables import info_key, getballistictrials, posturebias
from activitytables import crossingoffset, joinstepactivity, normalizeposition
from shuttlingplots import conditioncomparison, proxylegend
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

for i in range(21,22):
    offact = crossingoffset(cract,steps,i)
    offact.set_index(['subject','session'],inplace=True)
    normalizeposition(offact,inplace=True)
    stablebias,unstablebias = posturebias(offact,n=2)
    
    fig, (ax1,ax2) = plt.subplots(1,2)
    colors = ['b','cyan','orange','r']
    grouplabels = ['controls','small\nlesions','lesions','matched\ncontrols']
    conditions = [offact.query('stepstate3'),
                  offact.query('not stepstate3')]
    conditioncomparison('yhead',
                    [controls,small,lesions,matched],
                    conditions,colors=[colors[0],colors[-1]],
                    ax=ax1)
    proxylegend([colors[0],colors[-1]],['stable','unstable'],ax=ax1)
    ax1.set_xticklabels(grouplabels)
    ax1.set_ylim(-1,1)
    conditions = [stablebias.query('stepstate3'),
                  stablebias.query('not stepstate3'),
                  unstablebias.query('stepstate3'),
                  unstablebias.query('not stepstate3')]
    conditioncomparison('yhead',
                    [controls,small,lesions,matched],
                    conditions,colors=colors,
                    ax=ax2)
    proxylegend(colors,['stable [R]',
                        'stable [W]',
                        'unstable [W]',
                        'unstable [R]'],
                ax=ax2)
    xmin,xmax = ax2.get_xlim()
    ax2.set_xlim(xmin,xmax+8)
    ax2.set_xticklabels(grouplabels)
    ax2.set_ylim(-1,1)
    fig.suptitle(str.format('nose height {0} cm after crossing step',i))
plt.show()
    
# Save plot
