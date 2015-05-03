# -*- coding: utf-8 -*-
"""
Created on Sat May 02 15:06:05 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from shuttlingplots import averageposturecomparison
from datapath import lesionshamcache, crossings_key
from datapath import crossingactivity_stable_key
from datapath import crossingactivity_unstable_key

# Load data
stable = '(3 <= session < 5)'
unstable = '(9 <= session < 11)'
info = pd.read_hdf(lesionshamcache,info_key)
cr = pd.read_hdf(lesionshamcache,crossings_key).query('trial > 0')
scract = pd.read_hdf(lesionshamcache,crossingactivity_stable_key)
ucract = pd.read_hdf(lesionshamcache,crossingactivity_unstable_key)
cract = pd.concat([scract,ucract])
cract.reset_index(['subject','session','crossing'],inplace=True)

# Plot data
f, (ex1,ex2) = plt.subplots(1,2)
ex1cr1 = cr.query(str.format("subject == 'JPAK_21' and {0}",unstable))
ex1cr2 = cr.query(str.format("subject == 'JPAK_21' and {0}",stable))
averageposturecomparison(cract,info,ex1cr1,ex1cr2,ax=ex1)
ex1.set_title('Ca')
ex2cr1 = cr.query(str.format("subject == 'JPAK_24' and {0}",unstable))
ex2cr2 = cr.query(str.format("subject == 'JPAK_24' and {0}",stable))
averageposturecomparison(cract,info,ex2cr1,ex2cr2,ax=ex2)
ex2.set_title('Lb')
plt.show()

# Save plot
