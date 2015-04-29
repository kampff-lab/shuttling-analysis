# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:54:24 2015

@author: Gonçalo
"""

import activitytables
import shuttlingplots
import matplotlib.pyplot as plt
import pandas as pd

subjects = [r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_20',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_21',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_22',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_23',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_24',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_25',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_26',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_27',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_28',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_29',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_36',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_37',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_38',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_39',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_48',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_49',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_50',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_51',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_52',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_53',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_54',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_55']
            
decorticates = [r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_79',
                r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_81',
                r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_82']
            
# Figure 1
rr = activitytables.read_subjects(subjects,key=activitytables.rewards_key)
info = activitytables.read_subjects(subjects,key=activitytables.info_key)
cr = None
crd = None
infod = None

# Reward time over sessions
selection = 'session > 0 and session < 17'
shuttlingplots.timetoreward(rr.query(selection),info.query(selection))
ymin,ymax = plt.ylim()
plt.vlines(5*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(12*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(15*3+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)

# Time to cross over sessions
selection = "session < 17"
validcross = str.format('trial > 0 and {0}',selection)
shuttlingplots.timetocross(cr.query(validcross),info.query(selection))
locs,labels = plt.xticks()
labels = [l.get_text() for l in labels]
labels[0] = 'h'
plt.xticks(locs,labels)
ymin,ymax = plt.ylim()
plt.vlines(6*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(13*3+0.5,ymin,ymax,linestyles='solid')
plt.vlines(16*3+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)

# Time to cross over stable sessions (decorticates)
# Session protocol cleanup
crj = pd.concat([cr,crd])
infoj = pd.concat([info,infod])
infoj.ix[('JPAK_79',5),'protocol'] = 'stabletocenterfree'
infoj.ix[('JPAK_81',5),'protocol'] = 'stabletocenterfree'
infoj.ix[('JPAK_82',5),'protocol'] = 'stabletocenterfree'
#crj = cr
#infoj = info
selection = "session < 6"
validcross = str.format('trial > 0 and {0}',selection)
shuttlingplots.timetocross(crj.query(validcross),infoj.query(selection))
locs,labels = plt.xticks()
labels = [l.get_text() for l in labels]
labels[0] = '0'
plt.xticks(locs,labels)
ymin,ymax = plt.ylim()
ymax=45
plt.vlines(6*4+0.5,ymin,ymax,linestyles='solid')
plt.ylim(ymin,ymax)
