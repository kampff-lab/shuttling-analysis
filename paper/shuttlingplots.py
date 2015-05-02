# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:01:47 2015

@author: Gonçalo
"""

import datapath
import activitytables
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from activitytables import rail_start_cm, rail_stop_cm

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
    
def activitysummary(info,vcr_cache=None,cr_cache=None,ax=None):
    pooled = None
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        subjectpath = datapath.subjectpath(subject)
        rr = activitytables.read_subjects(subjectpath,days=[session],
                                          key=activitytables.rewards_key,
                                          includeinfokey=False)
        lpoke = activitytables.read_subjects(subjectpath,days=[session],
                                          key=[activitytables.leftpoke_key,
                                               activitytables.rewards_key],
                                          selector=activitytables.pokebouts,
                                          includeinfokey=False)
        rpoke = activitytables.read_subjects(subjectpath,days=[session],
                                          key=[activitytables.rightpoke_key,
                                               activitytables.rewards_key],
                                          selector=activitytables.pokebouts,
                                          includeinfokey=False)
        
        if vcr_cache is None:
            vcr = activitytables.read_subjects(subjectpath,days=[session],
                                               selector=activitytables.visiblecrossings,
                                               includeinfokey=False)
        else:
            vcr = vcr_cache.ix[(subject,session),:].set_index('index')
            
        if cr_cache is None:
            cr = activitytables.read_subjects(subjectpath,days=[session],
                                              selector=activitytables.crossings,
                                              includeinfokey=False)
        else:
            cr = cr_cache.ix[(subject,session),:].set_index('index')
            
        if len(rr) > 1:
            trialact = activitytables.trialactivity(rr,lpoke,rpoke,cr,vcr).sum()
            if pooled is None:
                pooled = trialact
            else:
                pooled += trialact

    pooled.ix[:-1].plot(kind='pie',ax=ax)
    
def averagetrajectory(cract,cr,ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    xpoints = np.linspace(rail_start_cm,rail_stop_cm,100)
    for subject,subcr in cr.groupby(level=['subject']):
        ypoints = activitytables.spatialinterp(xpoints,cract,subcr)
        #baseline = np.nanmean(ypoints[xpoints < 10])
        ymean = np.mean(ypoints,axis=0)
        yerr = stats.sem(ypoints,axis=0)
        ax.fill_between(xpoints,ymean-yerr,ymean+yerr,alpha=0.1)
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('y (cm)')
    ax.set_ylim(0,6)
    ax.set_xlim(5,45)
    
def skipprobability(cr,info,ax=None):
    skip = cr.steptime3.isnull() & cr.steptime4.isnull()
    skipfreq = skip.groupby(level=['subject']).sum()
    total = cr.groupby(level=['subject']).size()
    pskip = skipfreq / total
    pskip.name = 'skipfrequency'
    pskip = activitytables.groupbylesionvolumes(pskip,info,rename=True)
    pskip.reset_index('lesion',drop=True,inplace=True)
    ax = pskip.plot(kind='bar',ax=ax,grid=False,legend=False)
    ax.set_ylabel('p (skip middle steps)')
    ax.set_ylim(0,1)

def trajectorycluster(cr,ax=None,**kwargs):
    ax = cr.plot(x='duration',y='yhead_max',grid=False,ax=ax,
                 kind='scatter',marker='D',s=10,edgecolors='none',**kwargs)
    ax.set_xlabel('duration (s)')
    ax.set_ylabel('max height (cm)')
    ax.set_xlim(0,10)
    ax.set_ylim(0,21)
