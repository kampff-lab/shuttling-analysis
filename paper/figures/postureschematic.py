# -*- coding: utf-8 -*-
"""
Created on Sun May 03 19:36:10 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from shuttlingplots import medianposture
from datapath import lesionshamcache, stepfeatures_key

# Load data
info = pd.read_hdf(lesionshamcache,info_key)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key)

# Plot data
selection = "subject == 'JPAK_51' and session == 4 and side == 'rightwards'"
medianposture(steps.query(selection),info)
plt.show()

# Save plot
