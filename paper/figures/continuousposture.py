# -*- coding: utf-8 -*-
"""
Created on Mon Aug 03 14:06:38 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import flipleftwards, info_key
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import names, control, lesion, smalllesion, anylesion
from infotables import lesionordermap

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
info = pd.read_hdf(lesionshamcache, info_key)
lesionmap = lesionordermap(info)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smalllesions = str.format("subject in {0}",list(names(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
steps.xhead = flipleftwards(steps.xhead,steps.side)

# Plot data
steps = steps.query("subject != 'JPAK_20'")
fig, axes = plt.subplots(3,4)
for i,(s,d) in enumerate(steps.groupby(level='subject')):
    ax = axes[i / 4][i % 4]
    ticks = list(d.stepstate3.diff().nonzero()[0])
    ticks = ticks[1:4] + [ticks[-1]]
    d.xhead.plot(ax=ax,
                 style='.',
                 title=lesionmap[s],
                 xticks=ticks)
    ax.set_xticklabels(['ut','st','rd','all'])
    ax.set_ylim(0,8)
    ax.set_xlabel('trial')
    ax.set_ylabel('nose x (cm)')
plt.suptitle('step posture')
plt.tight_layout()
plt.show()

# Save plot
