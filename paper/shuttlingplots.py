# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:01:47 2015

@author: Gonçalo
"""

import activitytables
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

_splitprotocols_ = ['stabletocenterfree',
                    'centerfreetostable',
                    'randomizedcenterfree_day1']

def _sessionboxplot_(data,column=None,by=['session'],ax=None):
    box = data.boxplot(column,
                       by=by,
                       ax=ax,grid=False,
                       patch_artist=True,
                       return_type='dict')
    boxes = box[column]['boxes']
    numboxes = len(boxes)
    numsessions = numboxes / 3
    colors = ['b','mistyrose','r'] * numsessions
    for patch,color in zip(boxes,colors):
        patch.set_facecolor(color)
    plt.xlabel('session')
    plt.xticks(range(2,numboxes+1,3),range(0,numsessions,1))
    plt.legend(boxes[0:3],['control','small','lesion'],loc='upper left')
    
def _mergelesioncategory_(data,info):
    data = data.reset_index('sessionlabel')
    category = activitytables.lesioncategory(info)
    data = data.join(category)
    data.reset_index(inplace=True)
    return data
    
def _getsessionlabel_(session):
    return str.format("{0:02d}",session)
    
def _getsessionticklabels_(data):
    sessionlabels = data.sessionlabel.unique()
    sessionlabels.sort()
    return [label.lstrip('0').replace('a','pre').replace('b','')
            for label in sessionlabels]
    
def _reindexsessionlabels_(data,info,trialcolumn):
    result = []
    for datakey,datasession in data.groupby(level=['subject','session']):
        if info.ix[datakey,'protocol'] in _splitprotocols_:
            switch = datasession[trialcolumn] >= 20
            preswitch = [_getsessionlabel_(datakey[1])+'a'] * len(datasession[~switch])
            postswitch = [_getsessionlabel_(datakey[1])+'b'] * len(datasession[switch])
            sessionlabels = pd.Series(preswitch+postswitch,datasession.index)
        else:
            sessionlabels = [_getsessionlabel_(datakey[1])+'b']*len(datasession)
            sessionlabels = pd.Series(sessionlabels,datasession.index)
        sessionlabels.name = 'sessionlabel'
        result.append(sessionlabels)
    sessionlabels = pd.concat(result)
    data = pd.concat([data,sessionlabels],axis=1)
    data.reset_index(inplace=True)
    return data

def timetoreward(rr,info,ax=None):
    # Compute group mean reward times
    rr = _reindexsessionlabels_(rr,info,'index')
    grouplevel = ['subject','session','sessionlabel']
    rr.set_index(grouplevel,inplace=True)
    rrdiff = rr.groupby(level=grouplevel,sort=False)['time'].diff()
    rrdiff = rrdiff[~rrdiff.isnull()]
    rrsec = rrdiff.map(lambda x:x / np.timedelta64(1, 's')).to_frame()
    rrdata = rrsec.groupby(level=grouplevel).mean()
    rrdata.columns = ['rewards']
    
    # Merge lesion category column
    rrgdata = _mergelesioncategory_(rrdata,info)
    
    _sessionboxplot_(rrgdata,'rewards',by=['sessionlabel','category'],ax=ax)
    locs = plt.xticks()[0]
    labels = _getsessionticklabels_(rrgdata)
    plt.xticks(locs,labels)
    plt.ylabel('time between rewards (s)')
    
def timetocross(cr,info,ax=None):
    # Compute group means
    cr = _reindexsessionlabels_(cr,info,'trial')    
    grouplevel = ['subject','session','sessionlabel']
    crdata = cr.groupby(by=grouplevel,sort=False)['duration'].mean().to_frame()
    
    # Merge lesion category column
    crgdata = _mergelesioncategory_(crdata,info)
    
    _sessionboxplot_(crgdata,'duration',by=['sessionlabel','category'],ax=ax)
    locs = plt.xticks()[0]
    labels = _getsessionticklabels_(crgdata)
    plt.xticks(locs,labels)
    plt.ylabel('time to cross (s)')