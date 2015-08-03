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
colors = ['#FF000B','#FF0E00','#FF2801','#FF5C04','#FF8F06','#FFC108','#FFF309']
posturemean(steps.query('session == 5 and trial <= 20'),colors[-1],'S5*',ax=ax)
posturemean(steps.query('session == 5 and trial > 20'),colors[-2],'S5',ax=ax)
posturemean(steps.query('session == 6'),colors[-3],'S6',ax=ax)
posturemean(steps.query('session == 7'),colors[-4],'S7',ax=ax)
posturemean(steps.query('session == 8'),colors[-5],'S8',ax=ax)
posturemean(steps.query('session == 9'),colors[-6],'S9',ax=ax)
posturemean(steps.query('session == 10'),colors[-7],'S10',ax=ax)
plt.title('shift in posture across unstable sessions')
plt.xlim(3.4,5)
plt.ylim(1.6,3)
plt.show()

# Save plot
