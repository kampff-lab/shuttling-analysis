# -*- coding: utf-8 -*-
"""
Created on Sun May 03 18:12:44 2015

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
posturemean(steps.query('session == 0'),'r','H',ax=ax)
posturemean(steps.query('session == 1'),'m','S1',ax=ax)
posturemean(steps.query('session == 2'),'c','S2',ax=ax)
posturemean(steps.query('session == 3'),'g','S3',ax=ax)
posturemean(steps.query('session == 4'),'b','S4',ax=ax)
plt.xlim(3.4,5)
plt.ylim(1.6,3)
plt.show()

# Save plot
