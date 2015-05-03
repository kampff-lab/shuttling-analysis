# -*- coding: utf-8 -*-
"""
Created on Sun May 03 19:15:09 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from shuttlingplots import posturemean
from datapath import jumpers, lesionshamcache, stepfeatures_key

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)

# Plot data
fig = plt.figure()
ax = fig.gca()
posturemean(steps.query('session == 5 and trial <= 20'),'k','S5*',ax=ax)
posturemean(steps.query('session == 5 and trial > 20'),'r','S5',ax=ax)
posturemean(steps.query('session == 6'),'m','S6',ax=ax)
posturemean(steps.query('session == 7'),'y','S7',ax=ax)
posturemean(steps.query('session == 8'),'c','S8',ax=ax)
posturemean(steps.query('session == 9'),'g','S9',ax=ax)
posturemean(steps.query('session == 10'),'b','S10',ax=ax)
plt.xlim(3.4,5)
plt.ylim(1.6,3)
plt.show()

# Save plot
