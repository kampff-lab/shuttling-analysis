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
                    
_groupcolors_ = ['b','mistyrose','r','k']

def _groupboxplot_(data,column=None,by=['session'],ax=None):
    box = data.boxplot(column,
                       by=by,
                       ax=ax,grid=False,
                       patch_artist=True,
                       return_type='dict')
    numcategories = len(data.category.unique())
    mintick = (numcategories - 1) / 2.0
    boxes = box[column]['boxes']
    numboxes = len(boxes)
    numsessions = numboxes / numcategories
    colors = [_groupcolors_[i % numcategories] for i in range(numboxes)]
    for patch,color in zip(boxes,colors):
        patch.set_facecolor(color)
    plt.xticks(np.arange(mintick+1,numboxes+1,numcategories),
               range(0,numsessions,1))
    plt.legend(boxes[0:numcategories],
               ['control','small','lesion','decorticate'],
               loc='upper left')
    
def _mergelesioncategory_(data,info):
    category = activitytables.lesioncategory(info)
    data = data.join(category)
    data.reset_index(inplace=True)
    return data
    
def _getsessionlabel_(session):
    return str.format("{0:02d}",session)
    
def _getsessionticklabels_(data):
    sessionlabels = data.sessionlabel.unique()
    sessionlabels.sort()
    return [label.lstrip('0').replace('a','*').replace('b','')
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
    rrdata.reset_index('sessionlabel',inplace=True)
    rrgdata = _mergelesioncategory_(rrdata,info)
    
    _groupboxplot_(rrgdata,'rewards',by=['sessionlabel','category'],ax=ax)
    locs = plt.xticks()[0]
    labels = _getsessionticklabels_(rrgdata)
    plt.xticks(locs,labels)
    plt.xlabel('session')
    plt.ylabel('time between rewards (s)')
    
def timetocross_sessions(cr,info,ax=None):
    # Compute group means
    cr = _reindexsessionlabels_(cr,info,'trial')
    grouplevel = ['subject','session','sessionlabel']
    crdata = cr.groupby(by=grouplevel,sort=False)['duration'].mean().to_frame()
    
    # Merge lesion category column
    crdata.reset_index('sessionlabel',inplace=True)
    crgdata = _mergelesioncategory_(crdata,info)
    
    _groupboxplot_(crgdata,'duration',by=['sessionlabel','category'],ax=ax)
    locs = plt.xticks()[0]
    labels = _getsessionticklabels_(crgdata)
    plt.xticks(locs,labels)
    plt.xlabel('session')
    plt.ylabel('time to cross (s)')
    
def timetocross_trials(cr,info,ax=None):
    # Compute group means
    cr = cr.reset_index()
    grouplevel = ['subject','session','index']
    crdata = cr.groupby(by=grouplevel,sort=False)['duration'].mean().to_frame()
    
    # Merge lesion category column
    crdata.reset_index('index',inplace=True)
    crgdata = _mergelesioncategory_(crdata,info)
    
    _groupboxplot_(crgdata,'duration',by=['index','category'],ax=ax)
    plt.xlabel('trial')
    plt.ylabel('time to cross (s)')
