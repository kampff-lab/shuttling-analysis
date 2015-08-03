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
colors = ['#FF2801','#FF5C04','#FF8F06','#FFC108','#FFF309']
posturemean(steps.query('session == 0'),colors[-1],'H',ax=ax)
posturemean(steps.query('session == 1'),colors[-2],'S1',ax=ax)
posturemean(steps.query('session == 2'),colors[-3],'S2',ax=ax)
posturemean(steps.query('session == 3'),colors[-4],'S3',ax=ax)
posturemean(steps.query('session == 4'),colors[-5],'S4',ax=ax)
plt.title('shift in posture across stable sessions')
plt.xlim(3.4,5)
plt.ylim(1.6,3)
plt.show()

# Save plot
