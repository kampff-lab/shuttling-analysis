# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 18:02:49 2013

@author: gonca_000
"""

import itertools
import operator
import numpy as np

paths = np.array([r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_05-12_21/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_12-14_59/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_12-14_26/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_19-12_45/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_19-13_20/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_26-14_25/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_03-15_32/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_03-16_06/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_12-10_43/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_12-11_16/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_12-12_33/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_12-12_00/Analysis'])

annotationsfile = r'C:/Users/gonca_000/Desktop/BlindAnnotations.csv'
data = np.genfromtxt(annotationsfile,dtype=str,usecols=[0,1,2,3])

unscramblefile= r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/users/glopes/unscramble.txt'
unscramblekey = np.genfromtxt(unscramblefile,dtype=str)

def unscrambledindex(key):
    return np.nonzero(unscramblekey == key)[0][0]
    
scrambled = np.array([[key,list(grp)] for key,grp in itertools.groupby(data,key=operator.itemgetter(0))],dtype=object)
unscrambleidx = np.argsort(np.array([unscrambledindex(x[0].split('_',1)[1]) for x in scrambled]))
unscrambled = scrambled[unscrambleidx]

ethofiles = []
timestamps = None
for i,animal in enumerate(unscrambled):
    lines = []
    path = paths[i/2]
    if i%2 == 0:
        timestamps = np.genfromtxt(path + '/../front_video.csv',dtype=str)
    contact = np.genfromtxt(path + '/contact%s.csv' % ('' if i%2 == 0 else '2'),dtype=str)[1]
    lines.append('Contact %s\n' % (contact))
    contact = np.nonzero(timestamps == contact)[0][0]
    for filename,frame,evt,evttype in animal[1]:
        log = None
        frame = contact + int(frame) - 240
        time = timestamps[frame]
        if evt == 'C':
            log = 'Jump'
        if evt == 'I':
            log = 'ExploreRail' + ('Onset' if evttype == 'on' else 'Offset')
        if evt == 'B':
            log = 'Freeze' + ('Onset' if evttype == 'on' else 'Offset')
        if evt == 'R':
            log = 'Rear' + ('Onset' if evttype == 'on' else 'Offset')
        if log is not None:
            lines.append('%s %s\n' % (log,time))
    if 'Onset' in lines[-1]:
        lasttime = timestamps[contact + 1200]
        lastevt = lines[-1].split(' ',1)[0].replace('Onset','Offset')
        lines.append('%s %s\n' % (lastevt,lasttime))
    with open(path + '/blind_ethogram%s.csv' % ('' if i%2 ==0 else '2'),'w+') as f:
        f.writelines(lines)
    ethofiles.append(lines)
