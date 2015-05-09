# -*- coding: utf-8 -*-
"""
Created on Sat May 09 14:37:33 2015

@author: Gonçalo
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from infotables import names, lesionordermap
from activitytables import posturebias, info_key
from activitytables import normalize, mediannorm, flipleftwards
from shuttlingplots import proxylegend
from datapath import jumpers, lesionshamcache, stepfeatures_key
from datapath import crossingactivity_random_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
cract = pd.read_hdf(lesionshamcache,crossingactivity_random_key)
info = pd.read_hdf(lesionshamcache, info_key)
namemap = lesionordermap(info)
info = info.query(nonjumpers)
cract.reset_index(['subject','session','crossing'],inplace=True)

# Select data
bias = 2
group = list(names(info))
selection = str.format("subject in {0}",group)
random = '(session == 13 and trial > 20) or (14 <= session < 17)'
steps = steps.query(random).query(selection)
steps.xhead = flipleftwards(steps.xhead,steps.side)
normalize(steps,mediannorm,['xhead','yhead'],level=['subject'])
stablebias,unstablebias = posturebias(steps,n=bias)

stablebias = stablebias.query('stepstate3')
unstablebias = unstablebias.query('stepstate3')

sbact = cract.ix[stablebias.reset_index('time')['time'],:]
ubact = cract.ix[unstablebias.reset_index('time')['time'],:]
cract.reset_index(inplace=True)
endcrossing = cract.groupby(['subject','session','crossing']).last()
sbact.index.names = ['time']
ubact.index.names = ['time']
sbact.reset_index(inplace=True)
ubact.reset_index(inplace=True)
sbact.set_index(['subject','session','crossing'],inplace=True)
ubact.set_index(['subject','session','crossing'],inplace=True)
sbtimes = sbact.join(endcrossing,rsuffix='end')
ubtimes = ubact.join(endcrossing,rsuffix='end')
sbtimes['duration'] = (sbtimes.timeend - sbtimes.time) / np.timedelta64(1,'s')
ubtimes['duration'] = (ubtimes.timeend - ubtimes.time) / np.timedelta64(1,'s')
sbtimes['bias'] = 'Z'
ubtimes['bias'] = 'U'
sbtimes.reset_index(inplace=True)
ubtimes.reset_index(inplace=True)
sbtimes.subject = sbtimes.subject.apply(lambda x:namemap[x])
ubtimes.subject = ubtimes.subject.apply(lambda x:namemap[x])

# Plot data
names = sbtimes.subject.unique()
names.sort()
data = pd.concat([sbtimes,ubtimes])
box = data.boxplot('duration',by=['subject','bias'],grid=False,
                   patch_artist=True,return_type='dict')
boxes = box['duration']['boxes']
numboxes = len(boxes)
colors = ['orange' if i % 2 == 0 else 'dodgerblue' for i in range(numboxes)]
for patch,color in zip(boxes,colors):
    patch.set_facecolor(color)
plt.ylabel('time (s)')
plt.xticks(np.arange(1.5,len(names)*2,2),names)
proxylegend(['orange','dodgerblue'],['unstable bias','stable bias'])
plt.title('duration of trial after learning about stable state')
plt.ylim(0,5)
plt.show()
    
# Save plot
