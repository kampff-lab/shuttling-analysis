# -*- coding: utf-8 -*-
"""
Created on Sun May 03 18:12:44 2015

@author: Gonçalo
"""

import pandas as pd
import matplotlib.pyplot as plt
from activitytables import info_key
from shuttlingplots import posturemean
from datapath import jumpers, lesionshamcache, stepfeatures_key
from infotables import control, lesion, smalllesion, anylesion
from infotables import names, cagemates

# Load data
nonjumpers = str.format("subject not in {0}",jumpers)
steps = pd.read_hdf(lesionshamcache,stepfeatures_key).query(nonjumpers)
info = pd.read_hdf(lesionshamcache, info_key)
lesions = str.format("subject in {0}",list(names(lesion(info))))
smalllesions = str.format("subject in {0}",list(names(smalllesion(info))))
smallcontrols = str.format("subject in {0}",list(cagemates(smalllesion(info))))
alllesions = str.format("subject in {0}",list(names(anylesion(info))))
controls = str.format("subject in {0}",list(names(control(info))))

# Plot functions
def posturelearning(steps,title):
    fig = plt.figure()
    ax = fig.gca()
    colors = ['#FF2801','#FF5C04','#FF8F06','#FFC108','#FFF309']
    posturemean(steps.query('session == 0'),colors[-1],'H',ax=ax)
    posturemean(steps.query('session == 1'),colors[-2],'S1',ax=ax)
    posturemean(steps.query('session == 2'),colors[-3],'S2',ax=ax)
    posturemean(steps.query('session == 3'),colors[-4],'S3',ax=ax)
    posturemean(steps.query('session == 4'),colors[-5],'S4',ax=ax)
    plt.title('shift in posture across stable sessions')
    plt.suptitle(title)
    #plt.xlim(3.4,5)
    #plt.ylim(1.6,3)

# Plot data
posturelearning(steps,'all')
posturelearning(steps.query(lesions),'lesions')
posturelearning(steps.query(smalllesions),'small lesions')
posturelearning(steps.query(smallcontrols),'small controls')
posturelearning(steps.query(alllesions),'all lesions')
posturelearning(steps.query(controls),'controls')
plt.show()

# Save plot
