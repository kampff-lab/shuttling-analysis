# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 01:57:57 2013

@author: IntelligentSystems
"""

import os
import collections
import numpy as np
import analysis_utilities as utils
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch

event_color_scheme = collections.OrderedDict([
    ('normal',[0.75,0.75,0.75,1]),
    ('hesitate',[1,0,0,1]),
    ('investigate',[0,0,1,1]),
    ('compensate',[0,1,0,1]),
    ('rear',[0.48,0.41,0.65,1]),
    ('earFlick',[0,0,0,1]),
    ('leave',[1,1,1,1]),
    ('hesitatish',[1,0,0,0.50]),
    ('investigatish',[0,0,1,0.50]),
    ('compensatish',[0,1,0,0.50])
])

ethogram_file_name_mapping = {
    'Move':'normal',
    'Freeze':'hesitate',
    'ExploreRail':'investigate',
    'Jump':'compensate',
    'Rear':'rear',
    'EarFlick':'earFlick',
    'GoBack':'leave',
    'FinishAcross':'leave',
    'ExploreOriented':'investigatish',
    'FreezeOriented':'hesitatish',
    'JumpFlick':'compensatish'
}

#event_color_scheme ={
## 'Contact':[0,0,1,1],
# 'Move':[0.99,0.82,0.04,1],
# 'Rear':[0.48,0.41,0.65,1],
## 'GoBack':[0.27,0.47,0.13,1],
# 'Compensate':[0.2,0.54,0.74,1],
# 'Investigate':[0.09,0.52,0.53,1],
# 'EarFlick':[0.65,0.02,0.16,1],
# 'Bewildered':[0.81,0.27,0.34,1],
## 'FinishAcross':[0.27,0.47,0.13,1],
## 'Leave':[0.27,0.47,0.13,1],
#  'Leave':[0.5,0.5,0.5,1],
## 'Reward':[0.86,0.79,0.13,1]
#}

def get_timefile(path):
    timefile = os.path.join(path,'front_video.csv')
    if os.path.exists(timefile):
        return timefile
    path = os.path.split(path)[0]
    return get_timefile(path)

def load_ethogram(path):
    ethofile = np.genfromtxt(path,dtype=str)
    if len(np.shape(ethofile)) < 2:
        ethofile = np.array([ethofile])
    timefile = get_timefile(path)
    frame_time = np.genfromtxt(timefile,dtype=str)
    ethoframes = np.array([utils.index(frame_time,time[1]) for time in ethofile])
    ethoframes = ethoframes - ethoframes[0]
    return [(label,time,frame) for [label,time],frame in zip(ethofile,ethoframes)]
    
def get_ethogram_ranges(etho,scale=1):
    ranges = []
    ranges.append([])
    ranges.append([])
    ranges.append([])
    global event_color_scheme
    for i in range(len(etho)):
        name = etho[i][0]
        if name == 'Contact':
            continue
        if name.endswith('Offset'):
            continue        
        if name.endswith('Onset'):
            name = name[:-5]
            ranges[1].append([etho[i][2]*scale,(etho[i+1][2]-etho[i][2])*scale])
        else:
            if ethogram_file_name_mapping[name] == 'leave':
                duration = 300
            else:
                duration = 2*scale                
            ranges[1].append([etho[i][2]*scale,duration])
            
        name = ethogram_file_name_mapping[name]
        ranges[0].append(name)
        ranges[2].append(event_color_scheme[name])
        if name == 'leave':
            break
    return ranges
    
def plot_ethogram(etho,name,offset=0,legend=True):
    global event_color_scheme
    ranges = get_ethogram_ranges(etho,1/120.0)
    for ethoname,ethorange,ethocolor in zip(ranges[0],ranges[1],ranges[2]):
        if ethoname == 'earFlick':
            plt.vlines(ethorange[0],offset,offset+1,linewidth=2,linestyles='dotted')
        else:
            plt.broken_barh([ethorange],[offset,1],label=name,color=[ethocolor],linewidth=0)
    patches = [mpatch.Rectangle((0,0),1,1,fc=color) for color in event_color_scheme.itervalues()]
    if legend:
        plt.legend(patches,[c for c in event_color_scheme.iterkeys()],bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)