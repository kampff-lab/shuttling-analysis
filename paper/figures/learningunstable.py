# -*- coding: utf-8 -*-
"""
Created on Sun May 03 19:15:09 2015

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
    colors = ['#FF000B','#FF0E00','#FF2801','#FF5C04','#FF8F06','#FFC108','#FFF309']
    posturemean(steps.query('session == 5 and trial <= 20'),colors[-1],'S5*',ax=ax)
    posturemean(steps.query('session == 5 and trial > 20'),colors[-2],'S5',ax=ax)
    posturemean(steps.query('session == 6'),colors[-3],'S6',ax=ax)
    posturemean(steps.query('session == 7'),colors[-4],'S7',ax=ax)
    posturemean(steps.query('session == 8'),colors[-5],'S8',ax=ax)
    posturemean(steps.query('session == 9'),colors[-6],'S9',ax=ax)
    posturemean(steps.query('session == 10'),colors[-7],'S10',ax=ax)
    plt.title('shift in posture across unstable sessions')
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
