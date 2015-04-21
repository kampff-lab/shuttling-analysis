# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 13:11:39 2014

@author: Gonçalo
"""

import os
import cv2
import video
import imgproc
import pltutils
import numpy as np
import scipy as sp
import pandas as pd
import itertools as it
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import activitytables
import activityplots
import activitymovies
from preprocess import frames_per_second, steparea_pixels
from preprocess import labelpath, rail_start_cm, rail_stop_cm
from preprocess import max_width_cm, max_height_cm
from preprocess import stepcenter_cm, stepcenter_pixels
from collectionselector import CollectionSelector
from pandas.tools.plotting import scatter_matrix
from activitytables import getballistictrials
from activitytables import heightcutoff,cropstart,cropstop
from activitytables import heightfilter,positionfilter,speedfilter

# SCRIPTS
#figure1.featurecomparison(cr,['duration','xhead_speed_min','xhead_speed_max','xhead_speed_mean','xhead_speed_std'],'speed_features',r'C:\figs\featurecomparisons\speedfeatures',['duration','spd_min','spd_max','spd_mean','spd_std'])
#figure1.featurecomparison(cr,['yhead_min','yhead_max','yhead_mean',
#                              'yhead_std','xhead_speed_min','xhead_speed_max',
#                              'xhead_speed_mean','xhead_speed_std','duration'],
#                              'height_speed_features',
#                              r'C:\figs\featurecomparisons\heightspeedfeatures',
#                              ['y_min','y_max','y_mean',
#                              'y_std','s_min','s_max','s_mean','s_std','duration'])
colorcycle = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
protocolcolors = {
  'stable': 'b',
  'stabletocenterfree': {0b11111111:'b',0b11100111:'r'},
  'centerfree': 'r',
  'centerfreetostable': {0b11111111:'b',0b11100111:'r'},
  'randomizedcenterfree_day1': ['b']*20+['m'],
  'randomizedcenterfree_day2': 'm',
  'randomizedcenterfree_day3': 'm',
  'randomizedcenterfree_day4': 'm',
  'randomizedcenterfree_day5': 'm',
  'randomizedcenterfree_day6': 'm',
  'randomizedcenterfree_day7': 'm',
  'randomizedcenterfree_independent': 'm',
  'degradationrandomizedcenterfree_day1': ['b']*20+['m'],
  'degradationrandomizedcenterfree_day2': ['b']*20+['m'],
  'randomizedcenterfreetopermutation': ['m']*20+['y'],
  'randomizedcenterfreetofullyreleased': ['m']*20+['w'],
  'permutationfreepair_day1': 'y',
  'permutationfreepair_day2': 'y',
  'permutationfreepair_day3': 'y',
  'permutationfreepair_day4': 'y',
  'permutationtofullyreleased': {None:'y',0b10000001:'w'},
  'fullyreleased': 'w'
}

def buildtimetable(subjects,info,path):
    first = True
    #info = activitytables.read_subjects(subjects,key=activitytables.info_key)
    for spath,(subject,group) in zip(subjects,info.groupby(level=['subject'])):
        for session,sinfo in group.groupby(level=['session']):
            print str.format("Processing {0} {1}...",subject,session)
            hdf = pd.HDFStore(path)
            act = activitytables.read_subjects(spath,days=[session])
            act.reset_index(inplace=True)
            vidpath = os.path.join(spath,sinfo.dirname[0],'front_video.avi')
            act['path'] = vidpath
            act = act[['time','path','frame']]
            act.set_index('time',inplace=True)
            if first:
                hdf.put('timetable',act,format='table',data_columns=True)
                first = False
            else:
                hdf.append('timetable',act,format='table',data_columns=True)
            hdf.close()
                   
def getprotocolcolors(info):
    rows = []
    for key,row in info.iterrows():
        colorscheme = protocolcolors[row.protocol]
        if isinstance(colorscheme, dict):
            default = colorscheme.get(None)
            if default is not None:
                color = colorscheme.get(row.stepstate,default)
            else:
                color = colorscheme[row.stepstate]
        elif isinstance(colorscheme, list):
            index = int(min(row.trial,len(colorscheme)-1))
            color = colorscheme[index]
        else:
            color = colorscheme
        rows.append(color)
    return pd.DataFrame({'color':rows},info.index)

def preprocessing(cr,sact,scr,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    fig = plt.figure()
    plt.plot(cr.duration,cr.yhead_max,'.')
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title('all crossing trials')
    fname = 'crossings01.png'
    plt.savefig(os.path.join(path,fname))
    
    xmin,xmax = plt.xlim()
    plt.hlines((0,heightcutoff),xmin,xmax,'r')
    fname = 'crossings02.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    filtered = cr.query(heightfilter)
    plt.plot(filtered.duration,filtered.yhead_max,'.')
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title('filtered trials')
    fname = 'crossings03.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    for s in scr.slices.values:
        plt.plot(sact.xhead[s],sact.yhead[s],'k',alpha=0.1)
    plt.xlabel('x (cm)')
    plt.ylabel('y (cm)')
    plt.title('all nose trajectories')
    fname = 'crossings04.png'
    plt.savefig(os.path.join(path,fname))
    
    ymin,ymax = plt.ylim()
    plt.vlines((rail_start_cm,rail_stop_cm),ymin,ymax,'r')
    fname = 'crossings05.png'
    plt.savefig(os.path.join(path,fname))

    notpositionfilter = str.format('xhead_min < {0} or xhead_max > {1}',
                                   cropstart, cropstop)
    for s in scr.query(notpositionfilter).slices.values:
        plt.plot(sact.xhead[s],sact.yhead[s],'r')
    fname = 'crossings06.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    for s in scr.query(positionfilter).slices.values:
        plt.plot(sact.xhead[s],sact.yhead[s],'k',alpha=0.1)
    plt.xlabel('x (cm)')
    plt.ylabel('y (cm)')
    plt.title('filtered nose trajectories')
    fname = 'crossings07.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    filtered = filtered.query(positionfilter)
    plt.plot(filtered.duration,filtered.yhead_max,'.')
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title('filtered trials')
    fname = 'crossings08.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    plt.plot(filtered.duration,filtered.xhead_speed_25,'.')
    ymin,ymax = plt.ylim()
    plt.ylim(-10,ymax)
    plt.xlabel('duration (s)')
    plt.ylabel('speed Q1 (cm / s)')
    plt.title('speed 25th percentile')
    fname = 'crossings09.png'
    plt.savefig(os.path.join(path,fname))
    
    xmin,xmax = plt.xlim()
    plt.hlines(0,xmin,xmax,'r')
    fname = 'crossings10.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    filtered = filtered.query(speedfilter)
    plt.plot(filtered.duration,filtered.xhead_speed_25,'.')
    plt.xlabel('duration (s)')
    plt.ylabel('speed Q1 (cm / s)')
    plt.title('speed 25th percentile')
    fname = 'crossings11.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)
    
    fig = plt.figure()
    plt.plot(filtered.duration,filtered.yhead_max,'.')
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title('filtered trials')
    fname = 'crossings12.png'
    plt.savefig(os.path.join(path,fname))
    plt.close(fig)

def featurecomparison(cr,features,name,path,columns=None):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = cr[cr.trial > 0][features]
    if columns is not None:
        sessions.columns = columns
    sessions = sessions.groupby(level=['subject','session'])
    for (subject,session),group in sessions:
        scatter_matrix(group)
        plt.suptitle(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_{2}.png",
                           subject, session, name)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.savefig(fpath)
        plt.close('all')

def figure1b(rr,info,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    rr = rr.query('session > 0')
    info = info.query('session > 0')
    rrdiff = rr.groupby(level=[0,1]).diff()
    nulldiff = rrdiff.time.isnull()
    firstrr = rr.time[nulldiff] - info.starttime
    rrdiff.time[nulldiff] = firstrr
    rrsec = rrdiff.time.map(lambda x:x / np.timedelta64(1, 's'))
    rrdata = rrsec.groupby(level=[0,1]).mean()
    rryerr = rrsec.groupby(level=[0,1]).std()
    rrgdata = activitytables.groupbylesionvolumes(pd.concat([rrdata,rryerr],axis=1),info)
    
    plt.figure()
    activityplots.sessionmetric(rrgdata,colorcycle=['b','r'])
    plt.ylabel('time between rewards (s)')
    plt.title('performance curve')
    fname = 'performance_curve.png'
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
#    plt.close(fig)
    
def figure1b2(info,path,pooledtitle=None):
    if not os.path.exists(path):
        os.makedirs(path)
        
    pooled = None
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
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
        vcr = activitytables.read_subjects(subjectpath,days=[session],
                                           selector=activitytables.visiblecrossings,
                                           includeinfokey=False)
        cr = activitytables.read_subjects(subjectpath,days=[session],
                                          selector=activitytables.crossings,
                                          includeinfokey=False)
        if len(rr) > 1:
            trialact = activitytables.trialactivity(rr,lpoke,rpoke,cr,vcr).sum()
            if pooled is None:
                pooled = trialact
            else:
                pooled += trialact
            trialact.ix[:-1].plot(kind='pie')
        plt.title(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_trial_activity.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.savefig(fpath)
        plt.close(fig)

    if pooled is not None and pooledtitle is not None:
        fig = plt.figure()
        pooled.ix[:-1].plot(kind='pie')
        plt.title(pooledtitle)
        fname = str.format("{0}.png",pooledtitle)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)

def figure1c(cr,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    sessions = cr[cr.trial > 0].groupby(level=['subject','session'])
    for (subject,session),group in sessions:
        fig = plt.figure()
        
        plt.scatter(group.duration,group.yhead_max,
                    s=10,marker='D',facecolors='b',edgecolors='none')
        plt.xlim(0,25)
        plt.ylim(0,25)
        plt.xlabel('duration (s)')
        plt.ylabel('max height (cm)')
        plt.title(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_duration_maxheight.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
    sesscr = cr.query('trial > 0 and session > 0')
    subjectsessions = sesscr.groupby(level=['subject'])
    for subject,sessions in subjectsessions:
        fig = plt.figure()
        x = sessions.duration
        y = sessions.yhead_max
        color = plt.cm.copper(sessions.index.labels[1] / float(max(cr.index.labels[1]) + 1))
        plt.scatter(x,y,c=color,
                    s=10,marker='D',edgecolors='none')
        plt.xlim(0,25)
        plt.ylim(0,25)
        plt.xlabel('duration (s)')
        plt.ylabel('max height (cm)')
        plt.title(str.format('{0}',subject))
        fname = str.format("{0}_duration_maxheight_random.png",
                           subject)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
def __poolfeaturecomparison__(groups,path,colormap,labels,title,fname,alpha=1):
    if not os.path.exists(path):
        os.makedirs(path)
    
    fig = plt.figure()    
    for index,(name,group) in enumerate(groups):
        x = group.duration
        y = group.yhead_max
        try:
            color = np.asarray(colormap)[index % len(colormap)]
        except IndexError:
            color = colormap(index / len(groups))
        plt.scatter(x,y,c=color,
                    s=10,edgecolors='none',
                    label=labels[index] if labels is not None else None,
                    alpha=alpha)
    plt.xlim(0,10)
    plt.ylim(0,21)
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title(title)
    plt.legend()
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
    
def figure1c0(cr,path,alpha=1,color='b',label=None,
              fname='all_subjects_duration_maxheight.png'):
    groups = cr[cr.trial > 0]
    __poolfeaturecomparison__([('crossings',groups)],path,[color],label,
                              'crossing duration vs height',
                              fname,alpha=alpha)
        
def figure1c2(cr,path,alpha=1,
              fname='all_subjects_duration_maxheight_conditions.png'):
    groups = cr[cr.trial > 0].groupby(level=['session'])
    __poolfeaturecomparison__(groups,path,['b','r','g'],
                              ['stable','partial','unstable'],
                              'crossing duration vs height',
                              fname,alpha=alpha)
                              
def figure1c3(cr,info,path,alpha=1,
              fname='all_subjects_duration_maxheight_lesion.png'):
    lesioninfo = (info.lesionleft + info.lesionright) > 0
    lesioninfo.name = 'lesion'
    cr = cr.join(lesioninfo)
    groups = cr[cr.trial > 0].groupby(by=['lesion'])
    __poolfeaturecomparison__(groups,path,['b','r'],
                              ['control','lesion'],
                              'crossing duration vs height',
                              fname,alpha=alpha)
                              
def figure1c4(cr,info,path,alpha=1,
              fname='all_subjects_duration_maxheight_big_lesion.png'):
    lesioninfo = (info.lesionleft + info.lesionright) > 15
    lesioninfo.name = 'lesion'
    cr = cr.join(lesioninfo)
    groups = cr[cr.trial > 0].groupby(by=['lesion'])
    __poolfeaturecomparison__(groups,path,['b','r'],
                              ['control+small','big lesion'],
                              'crossing duration vs height',
                              fname,alpha=alpha)
                              
def figure1c5(cr,info,path,alpha=1,
              fname='all_subjects_duration_maxheight_weight.png'):
    weightinfo = info.weight < 250
    weightinfo.name = 'weight'
    cr = cr.join(weightinfo)
    groups = cr[cr.trial > 0].groupby(by=['weight'])
    __poolfeaturecomparison__(groups,path,['b','r'],
                              ['normal','lightweight'],
                              'crossing duration vs height',
                              fname,alpha=alpha)
                              
def figure1c6(cr,info,path,alpha=1,
              fname='all_subjects_duration_maxheight_gender.png'):
    genderinfo = info.gender == 'male'
    genderinfo.name = 'gender'
    cr = cr.join(genderinfo)
    groups = cr[cr.trial > 0].groupby(by=['gender'])
    __poolfeaturecomparison__(groups,path,['b','r'],
                              ['female','male'],
                              'crossing duration vs height',
                              fname,alpha=alpha)
    
def resetsessionindex(cr,labels,fillvalue=None):
    reset = cr.reset_index('session')
    sessionlabels = reset.session.unique()
    for sessionlabel,label in it.izip_longest(sessionlabels,
                                              labels,fillvalue=fillvalue):
        reset.session[reset.session == sessionlabel] = label
    reset.set_index('session',append=True,inplace=True)
    return reset
    
def __poolfeature__(feature,ylabel,title,fname,cr,info,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    cut = getballistictrials(cr)
    m = cut.groupby(level=['subject','session'])[feature].mean()
    e = cut.groupby(level=['subject','session'])[feature].std()
    d = activitytables.groupbylesionvolumes(pd.concat([m,e],axis=1),info)
    fig = plt.figure()
    ax = plt.gca()
    activityplots.sessionmetric(d,ax=ax,colorcycle=colorcycle)
    plt.ylabel(ylabel)
    plt.title(title)
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
    
def __poolfeatureconditions__(feature,conditions,ylabel,title,fname,cr,info,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    labels = range(len(conditions))
    cr = resetsessionindex(cr,labels,labels[-1])
    info = resetsessionindex(info,labels,labels[-1])
    cut = getballistictrials(cr)
    m = cut.groupby(level=['subject','session'])[feature].mean()
    e = cut.groupby(level=['subject','session'])[feature].std()
    d = activitytables.groupbylesionvolumes(pd.concat([m,e],axis=1),info)
    fig = plt.figure()
    ax = plt.gca()
    activityplots.sessionmetric(d,ax=ax,colorcycle=colorcycle,connect=True)
    plt.xlabel('')
    plt.xticks(labels,conditions)
    plt.ylabel(ylabel)
    plt.title(title)
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
        
def figure1d(cr,info,path):
    __poolfeature__('duration','time to cross (s)',
                    'time to cross obstacles','time_curve.png',
                    cr,info,path)
    
def figure1d2(cr,info,path):
    __poolfeatureconditions__('duration',['stable','partial','unstable'],
                              'time to cross (s)','time to cross obstacles',
                              'time_curve_conditions.png',
                              cr,info,path)
    
def figure1e(cr,info,path):
    __poolfeature__('yhead_mean','nose height (cm)',
                    'average nose height','height_curve.png',
                    cr,info,path)
                    
def figure1e2(cr,info,path):
    __poolfeatureconditions__('yhead_mean',['stable','partial','unstable'],
                              'nose height (cm)','average nose height',
                              'height_curve.png',
                              cr,info,path)

def __spatialaveragesbysession__(subjects,cr,path,selector=lambda x:x.yhead,
                                 ylabel='y (cm)',xlim=None,ylim=None):
    if not os.path.exists(path):
        os.makedirs(path)
    
    cut = getballistictrials(cr)
    sessions = cut[cut.trial > 0].groupby(level=['session'])
    for session,group in sessions:
        fig = plt.figure()
        sact = activitytables.read_subjects(subjects,days=[session])
        
        x,y,yerr = activitytables.spatialaverage(sact,group,selector)
        activityplots.trajectoryplot(sact,group,alpha=0.2,flip=True,
                                     selector=selector)
        plt.fill_between(x,y-yerr,y+yerr)
        
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel('x (cm)')
        plt.ylabel(ylabel)
        plt.title(str.format('session {0}',session))
        fname = str.format("session_{0}_trajectories.png",
                           session)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
def __spatialaveragesoverlay__(cr,path,selector=lambda x:x.yhead,
                               ylabel='y (cm)',xlim=None,ylim=None):
    if not os.path.exists(path):
        os.makedirs(path)
    
    fig = plt.figure()
    cut = getballistictrials(cr)
    sessions = cut[cut.trial > 0].groupby(level=['subject'])
    days = cut.index.levels[1][cut.index.labels[1]].unique()
    for subject,group in sessions:
        print str.format("Processing {0}...",subject)
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=days)
        
        x,y,yerr = activitytables.spatialaverage(sact,group,selector)
        plt.fill_between(x,y-yerr,y+yerr)
        
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel('x (cm)')
        plt.ylabel(ylabel)
        
    plt.title(str.format('average trajectories'))
    fname = str.format("average_trajectories.png")
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
    
def __spatialaverages__(cr,path,selector=lambda x:x.yhead,
                        ylabel='y (cm)',xlim=None,ylim=None):
    if not os.path.exists(path):
        os.makedirs(path)
    
    cut = getballistictrials(cr)
    sessions = cut[cut.trial > 0].groupby(level=['subject','session'])
    for (subject,session),group in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        
        x,y,yerr = activitytables.spatialaverage(sact,group,selector)
        activityplots.trajectoryplot(sact,group,alpha=0.2,flip=True,
                                     selector=selector)
        plt.fill_between(x,y-yerr,y+yerr)
        
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel('x (cm)')
        plt.ylabel(ylabel)
        plt.title(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_trajectories.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.savefig(fpath)
        plt.close(fig)

def figure1f(cr,path):
    __spatialaverages__(cr,path,xlim=(5,45),ylim=(0,7))
    
def __spatialaveragecomparison__(cr,path,selector=lambda x:x.yhead,
                                 ylabel='y (cm)',xlim=None,ylim=None):
    if not os.path.exists(path):
        os.makedirs(path)
    
    cut = getballistictrials(cr)
    conditions = cut[cut.trial > 0].groupby(level=['subject'])
    for subject,group in conditions:
        fig = plt.figure()
        
        days = group.index.levels[1][group.index.labels[1]].unique()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        act = activitytables.read_subjects(subjectpath,days=days)
    
        stact = act[act.stepstate3]
        stcr = group[group.stepstate3]
        x,y,yerr = activitytables.spatialaverage(stact,stcr,selector)
        plt.fill_between(x,y-yerr,y+yerr,color='b')
        
        uact = act[~act.stepstate3]
        ucr = group[~group.stepstate3]
        x,y,yerr = activitytables.spatialaverage(uact,ucr,selector)
        plt.fill_between(x,y-yerr,y+yerr,color='r')
        
        p1 = plt.Rectangle((0, 0), 1, 1, fc='b')
        p2 = plt.Rectangle((0, 0), 1, 1, fc='r')
        plt.legend([p1, p2], ['stable', 'unstable'])
        
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel('x (cm)')
        plt.ylabel(ylabel)
        plt.title(str.format('{0} trajectories',subject))
        fname = str.format("{0}_trajectories_stable_unstable.png",subject)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1f2(cr,path):
    __spatialaveragecomparison__(cr,path,xlim=(5,45),ylim=(0,7))
    
def figure1f3(cr,path):
    return __spatialaveragesoverlay__(cr,path,xlim=(5,45),ylim=(0,7))
        
def figure1h(cr,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    cut = getballistictrials(cr)
    conditions = cut[cut.trial > 0].groupby(level=['subject'])
    for subject,group in conditions:
        fig = plt.figure()
        entryspeed = group.entryspeed
        crossingspeed = group.crossingspeed
        plt.plot(entryspeed,crossingspeed,'.')
        pltutils.regressionline(entryspeed,crossingspeed,color='k')
        plt.xlabel('entry speed (cm / s)')
        plt.ylabel('crossing speed (cm / s)')
        plt.title('slowdown')
        fname = str.format("{0}_slowdown_stable.png",subject)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1i(cr,path):
    __spatialaverages__(cr,path,selector=lambda x:x.xhead_speed.abs(),
                        ylabel='abs. speed (cm / s)',
                        xlim=(5,45),ylim=(0,150))
                        
def figure1i2(cr,path):
    __spatialaveragecomparison__(cr,path,selector=lambda x:x.xhead_speed.abs(),
                        ylabel='abs. speed (cm / s)',
                        xlim=(5,45),ylim=(0,150))
                        
def figure1j(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    fig = plt.figure()
    sessions = info.groupby(level=['subject'])
    xticks = []
    xticklabels = []
    barplotwidth = 4
    for i,(subject,sinfo) in enumerate(sessions):
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = sinfo.index.levels[1][sinfo.index.labels[1]]
        act = activitytables.read_subjects(subjectpath,days=days)
        cr = activitytables.read_subjects(subjectpath,days=days,
                                          selector=activitytables.crossings)
        offset = i * barplotwidth
                                          
        stact = act[act.stepstate3]
        stcr = cr[cr.stepstate3]
        stfeatures = activitytables.stepfeature(stact,stcr,4,3)
        stskipfrequency = 1 - float(len(stfeatures)) / len(stcr)
        
        uact = act[~act.stepstate3]
        ucr = cr[~cr.stepstate3]
        ufeatures = activitytables.stepfeature(uact,ucr,4,3)
        uskipfrequency = 1 - float(len(ufeatures)) / len(ucr)
        plt.bar((-1 + offset,offset),(stskipfrequency,uskipfrequency),
                color=['b','r'],width=1,hold=True)
        
        xticks.append(offset)
        xticklabels.append(subject.replace('JPAK_',''))

    p1 = plt.Rectangle((0, 0), 1, 1, fc="b")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="r")
    plt.legend([p1,p2],['stable', 'unstable'],
               bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.)
    
    plt.xlabel('subject (JPAK)')
    plt.ylabel('p(skipping)')
    plt.xticks(xticks,xticklabels)
    plt.xlim(-2,len(sessions) * barplotwidth - 1)
    #plt.title(str.format('4th step contact frequency',subject))
    fname = str.format("all_animals_4thstep_frequency.png",subject)
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)

def figure1k(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        activityplots.clusterstepframes(sact,sinfo,4,3)
        
        plt.suptitle(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_step_posture.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        
        fig = plt.gcf()
        plt.get_current_fig_manager().resize(1090,480)
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1n(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        activityplots.clusterslipframes(sact,sinfo,4,2)
        
        plt.suptitle(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_slip_posture.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        
        fig = plt.gcf()
        plt.get_current_fig_manager().resize(1090,480)
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1k1(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        scr = activitytables.read_subjects(subjectpath,days=[session],
                                           selector = activitytables.crossings)
        features = activitytables.stepfeature(sact,scr,4,3)
        leftwards = features.side == 'leftwards'
        features.xhead[leftwards] = max_width_cm - features.xhead[leftwards]
        median = np.sort(features.xhead)[len(features)/2+1]
        median = features[features.xhead == median].iloc[-1,:]
        
        vidpaths = activitymovies.getmoviepath(sinfo)
        timepaths = activitymovies.gettimepath(info)
        movie = [video.video(mpath,mtimepath)
                 for mpath,mtimepath in zip(vidpaths,timepaths)][0]
        medianframe = movie.frame(sact.index.get_loc(median.name))
        flip = median.side == 'rightwards'
        stepindex = 3 if flip else 4
        medianframe = activitytables.cropstep(medianframe,stepindex,flip=flip)
        
        fname = str.format("{0}_session_{1}_median_step_posture.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        cv2.imwrite(fpath,medianframe)
        
def figure1k2(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        scr = activitytables.read_subjects(subjectpath,days=[session],
                                           selector = activitytables.crossings)
        stepframes = activitytables.stepframes(sact,scr,sinfo,4,3)
        side = int(np.ceil(np.sqrt(len(stepframes))))
        tile = imgproc.tile(stepframes,side,side)
        plt.imshow(tile[0], cmap = plt.cm.Greys_r)
        plt.title(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_step_posture.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.axis("off")
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1n2(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject','session'])
    for (subject,session),sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        sact = activitytables.read_subjects(subjectpath,days=[session])
        scr = activitytables.read_subjects(subjectpath,days=[session],
                                           selector = activitytables.crossings)
        slipframes = activitytables.slipframes(sact,scr,sinfo,3,3)
        side = int(np.ceil(np.sqrt(len(slipframes))))
        tile = imgproc.tile(slipframes,side,side)
        plt.imshow(tile[0], cmap = plt.cm.Greys_r)
        plt.title(str.format('{0} (session {1})',subject,session))
        fname = str.format("{0}_session_{1}_slip_posture.png",
                           subject, session)
        fpath = os.path.join(path,subject)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        fpath = os.path.join(fpath,fname)
        plt.axis("off")
        plt.savefig(fpath)
        plt.close(fig)
        
def _averageposture_(info,subjectpath,cropsize=(300,300)):
    if len(info) == 0:
        return np.zeros(cropsize,dtype=np.float32)
    stepframes = []
    for key,group in info.groupby(level=['session']):
        act = activitytables.read_subjects(subjectpath,days=[key])
        cr = activitytables.read_subjects(subjectpath,days=[key],
                                            selector = activitytables.crossings)
        stepframes += activitytables.stepframes(act,cr,group,4,3,
                                                cropsize=cropsize,
                                                subtractBackground=True)
    stepframes = [cv2.threshold(f, 5, 255, cv2.cv.CV_THRESH_BINARY)[1]
                  for f in stepframes]
    return imgproc.average(stepframes,1)
        
def figure1k3(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject'])
    for subject,sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        
        stinfo = sinfo[sinfo.protocol == 'stable']
        stavg = _averageposture_(stinfo,subjectpath)
        
        uinfo = sinfo[sinfo.protocol == 'centerfree']
        uavg = _averageposture_(uinfo,subjectpath)
        
        rinfo = sinfo[sinfo.protocol.str.contains('randomizedcenterfree')]
        ravg = _averageposture_(rinfo,subjectpath)
        
        avg = cv2.merge((uavg,stavg,ravg))
        avg = avg.astype(np.uint8)
        avg = cv2.convertScaleAbs(avg,alpha=1.4,beta=0.0)
        plt.imshow(avg)
        plt.title(str.format('{0}',subject))
        fname = str.format("{0}_posture_stable_unstable.png", subject)
        fpath = os.path.join(path,fname)
        plt.axis("off")
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1k4(info,path):
    if not os.path.exists(path):
        os.makedirs(path)

    sessiondata = []
    sessionyerr = []
    sessions = info.groupby(level=['subject'])
    for i,(subject,sinfo) in enumerate(sessions):
        print str.format("Processing {0}...",subject)
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = sinfo.index.levels[1][sinfo.index.labels[1]]

#        act,cr,fcr,info = activitytables.read_canonical(subjectpath,days=days)
#        slipactivity = activitytables.slipactivity(act,cr)
#        slipactivity = slipactivity[slipactivity.trial > 0]
        
        act = activitytables.read_subjects(subjectpath,days=days)
        slipactivity = activitytables.slipactivity(act).join(act)
        slipactivity = slipactivity[slipactivity.trial > 0]
        
        slipevents = activitytables.countslipevents(slipactivity)
        slipspertrial = slipevents.groupby(level=['subject','session',
                                                  'trial']).sum()
        slipmean = slipspertrial.groupby(level=('subject','session')).mean()
        slipstd = slipspertrial.groupby(level=('subject','session')).std()
        sessiondata.append(slipmean)
        sessionyerr.append(slipstd)
    return sessiondata,sessionyerr
        
def figure1l(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject'])
    for subject,sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = sinfo.index.levels[1][sinfo.index.labels[1]].unique()
        act = activitytables.read_subjects(subjectpath,days=days)
        cr = activitytables.read_subjects(subjectpath,days=days,
                                          selector=activitytables.crossings)
        
        axScatter = plt.subplot2grid((3,3),(1,0),rowspan=2,colspan=2)
        axHistx = plt.subplot2grid((3,3),(0,0),colspan=2)
        axHisty = plt.subplot2grid((3,3),(1,2),rowspan=2)
        axes = (axScatter,axHistx,axHisty)
        stepoffset = stepcenter_cm[3][1]
        bins = 50
        xlim = (20-stepoffset,30-stepoffset)
        ylim = (-1,9)
        alpha = 0.75
                                          
        stact = act[act.stepstate3]
        stcr = cr[cr.stepstate3]
        stfeatures = activitytables.stepfeature(stact,stcr,4,3)
        leftwards = stfeatures.side == 'leftwards'
        stfeatures.xhead[leftwards] = max_width_cm - stfeatures.xhead[leftwards]
        stfeatures.xhead -= stepoffset
        
        uact = act[~act.stepstate3]
        ucr = cr[~cr.stepstate3]
        ufeatures = activitytables.stepfeature(uact,ucr,4,3)
        leftwards = ufeatures.side == 'leftwards'
        ufeatures.xhead[leftwards] = max_width_cm - ufeatures.xhead[leftwards]
        ufeatures.xhead -= stepoffset
        
        activityplots.scatterhist(stfeatures.xhead,stfeatures.yhead,color='b',
                                  bins=bins,axes=axes,xlim=xlim,ylim=ylim,
                                  histalpha=alpha)
        activityplots.scatterhist(ufeatures.xhead,ufeatures.yhead,color='r',
                                  bins=bins,axes=axes,xlim=xlim,ylim=ylim,
                                  histalpha=alpha)
        axScatter.set_xlabel('x (cm)')
        axScatter.set_ylabel('y (cm)')
        axScatter.legend(['stable', 'unstable'],loc=2)
        
        axHistx.set_title(str.format('{0} nose position on contact',subject))
        fname = str.format("{0}_nose_stable_unstable.png",subject)
        fpath = os.path.join(path,fname)
        plt.savefig(fpath)
        plt.close(fig)
        
def _zscoresubjects_(data):
    result = []
    sessions = data.groupby(level=['subject'],sort=False)
    for subject,sdata in sessions:
        zdata = activitytables.zscore(sdata)
        result.append(zdata)
    return pd.concat(result)
        
def __concatstepslices__(slices):
    subjects = []
    for sub in slices:
#        for i,crossing in enumerate(sub):
#            crossing['crossindex'] = i
        subjects.append(pd.concat(sub))
    return pd.concat(subjects)
    
def _extractallstepfeatures_(info):
    sessions = info.groupby(level=['subject'])
    subjects = []
    for subject,group in sessions:
        print str.format("Processing {0}...", subject)
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = group.index.levels[1][group.index.labels[1]].unique()
        act = activitytables.read_subjects(subjectpath,days=days)
        cr = activitytables.read_subjects(subjectpath,days=days,
                                          selector=activitytables.crossings)
        features = activitytables.stepfeature(act,cr,4,3)
        subjects.append(features)
    return pd.concat(subjects)
    
def _extractallstepslices_(stepfeatures,before=200,after=400):
    sessions = stepfeatures.groupby(level=['subject'])
    subjects = []
    for subject,group in sessions:
        print str.format("Processing {0}...", subject)
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = group.index.levels[1][group.index.labels[1]].unique()
        act = activitytables.read_subjects(subjectpath,days=days)
        subslices = _extractstepslice_(act,group,before,after)
        subjects.append(subslices)
    return pd.concat(subjects)

def _extractstepslice_(act,stepfeatures,before=200,after=400):
    slices = []
    for i,(index, row) in enumerate(stepfeatures.iterrows()):
        ix = act.index.get_loc(index)
        ixslice = slice(ix-before,ix+after+1)
        actslice = act.ix[ixslice]
        actslice['side'] = row.side
        actslice['crossindex'] = i
        actslice['frameindex'] = range(ixslice.stop - ixslice.start)
        slices.append(actslice)
    return pd.concat(slices)
        
def _extractstepfeatures_(info,stf=None,uf=None,stepoffset=0):
    pooledst = []
    pooledu = []
    sessions = info.groupby(level=['subject'])
    for subject,sinfo in sessions:
        print str.format("Processing {0}...", subject)
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = sinfo.index.levels[1][sinfo.index.labels[1]].unique()
        
        if stf is None and uf is None:
            act = activitytables.read_subjects(subjectpath,days=days)
            cr = activitytables.read_subjects(subjectpath,days=days,
                                              selector=activitytables.crossings)
            stact = act[act.stepstate3]
            stcr = cr[cr.stepstate3]
            stfeatures = activitytables.stepfeature(stact,stcr,4,3)
            uact = act[~act.stepstate3]
            ucr = cr[~cr.stepstate3]
            ufeatures = activitytables.stepfeature(uact,ucr,4,3)
        else:
            stfeatures = stf.query(str.format("subject == '{0}'",subject))
            if len(uf) > 0:
                ufeatures = uf.query(str.format("subject == '{0}'",subject))
            else:
                ufeatures = pd.DataFrame()
        
        leftwards = stfeatures.side == 'leftwards'
        stfeatures.xhead[leftwards] = max_width_cm - stfeatures.xhead[leftwards]
        stfeatures.xhead -= stepoffset
        pooledst.append(stfeatures)
        
        if len(ufeatures) > 0:
            leftwards = ufeatures.side == 'leftwards'
            ufeatures.xhead[leftwards] = max_width_cm - ufeatures.xhead[leftwards]
            ufeatures.xhead -= stepoffset
            pooledu.append(ufeatures)
    return pooledst,pooledu

def figure1l2(info,path,stf=None,uf=None,name=None,title=None,
              xlim=(20,30),ylim=(-1,9),histxmax=200,histymax=200):
    if not os.path.exists(path):
        os.makedirs(path)

    fig = plt.figure()
    axScatter = plt.subplot2grid((3,3),(1,0),rowspan=2,colspan=2)
    axHistx = plt.subplot2grid((3,3),(0,0),colspan=2)
    axHisty = plt.subplot2grid((3,3),(1,2),rowspan=2)
    axes = (axScatter,axHistx,axHisty)
    stepoffset = stepcenter_cm[3][1]
#    bins = 50
    binsize = 0.2
    xlim = (xlim[0]-stepoffset,xlim[1]-stepoffset)
    #xlim = (20-stepoffset,48-stepoffset) # For MULTI-TIMES
    #xlim = (20-stepoffset,30-stepoffset) # For CONTACT
    bins = np.arange(xlim[0],xlim[1]+binsize,binsize)
    #ylim = (-1,9)
    histalpha = 0.75
    scatteralpha = 0.4
#    histxmax = 250
#    histymax = 250
#    histymax = 350
    pooledst,pooledu = _extractstepfeatures_(info,stf,uf,stepoffset)
    
#    xlim=(-1,200)
#    ylim=(-150,150)
    
    stfeatures = pd.concat(pooledst)
    activityplots.scatterhist(stfeatures.xhead,stfeatures.yhead,color='b',
                              bins=bins,axes=axes,xlim=xlim,ylim=ylim,
                              histalpha=histalpha,alpha=scatteralpha)
                              
    if len(pooledu) > 0:
        ufeatures = pd.concat(pooledu)
        activityplots.scatterhist(ufeatures.xhead,ufeatures.yhead,color='r',
                                  bins=bins,axes=axes,xlim=xlim,ylim=ylim,
                                  histalpha=histalpha,
                                  alpha=scatteralpha)
    axScatter.set_xlabel('x (cm)')
    axScatter.set_ylabel('y (cm)')
    axScatter.legend(['stable', 'unstable'],loc=2)
    
    suffix = '' if name is None else name
    titlesuffix = suffix if title is None else title
    title = str.format('nose position on contact ({0})',titlesuffix)
    axHistx.set_title(title)
    axHistx.set_ylim(0,histxmax)
    axHisty.set_xlim(0,histymax)
    fname = str.format("nose_stable_unstable_{0}.png",suffix)
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.clf()
    plt.close(fig)
    
def figure1l3(info,path,ixsts,uxsts,numtimepoints=15,offset=200,delta=5,
              xlim=(20,30),ylim=(-1,9),histxmax=200,histymax=200):
    squery = info.index.levels[0][info.index.labels[0]].unique()
    squery = repr(squery).replace('array(','').replace(', dtype=object)','').replace('\n','')
    ixsts = ixsts.query(str.format("subject in {0}",squery))
    if len(uxsts) > 0:
        uxsts = uxsts.query(str.format("subject in {0}",squery))
        
    for i in range(numtimepoints):
        frameindex = offset + i * delta
        frametime = (frameindex - 200) * 1000.0 / frames_per_second
        suxsts = uxsts
        if len(uxsts) > 0:
            suxsts = uxsts[uxsts.frameindex == frameindex]
        sixsts = ixsts[ixsts.frameindex == frameindex]
        figure1l2(info,
                  path,
                  sixsts,
                  suxsts,
                  str.format("{0}ms",int(frametime)),
                  str.format("{0:.2f} ms",frametime),
                  xlim=xlim,ylim=ylim,
                  histxmax=histxmax,histymax=histymax)
        
def figure1o(info,path,tile=False):
    if not os.path.exists(path):
        os.makedirs(path)

    trials = []
    preoffset = 60
    postoffset = 180
    time = np.arange(-preoffset,+postoffset) / frames_per_second
    for subject,subinfo in info.groupby(level=['subject']):
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        for protocol,sinfo in subinfo.groupby('protocol',sort=False):
            fbase = os.path.join(path,protocol)
            if not os.path.exists(fbase):
                os.makedirs(fbase)
            
            fig = plt.figure()
            days = sinfo.index.levels[1][sinfo.index.labels[1]].unique()
            print str.format("Processing {0} {1}...", subject, protocol)
            act = activitytables.read_subjects(subjectpath,days=days,includeinfokey=False)
            cr = activitytables.read_subjects(subjectpath,days=days,
                                          selector=activitytables.fullcrossings,
                                          includeinfokey=False)
            trialr = cr.steptime3[cr.side == 'rightwards']
            triall = cr.steptime4[cr.side == 'leftwards']
            trialr = trialr[~trialr.isnull()]
            triall = triall[~triall.isnull()]
            idxr = [act.index.get_loc(act.index.asof(t)) for t in trialr]
            idxl = [act.index.get_loc(act.index.asof(t)) for t in triall]
            ssr = [slice(i-preoffset,i+postoffset) for i in idxr[1:]]
            ssl = [slice(i-preoffset,i+postoffset) for i in idxl[1:]]
            stepactr = np.array([act.stepactivity3[s] for s in ssr],np.float).T
            stepactl = np.array([act.stepactivity4[s] for s in ssl],np.float).T
            stepactr /= steparea_pixels[3] * 255
            stepactl /= steparea_pixels[4] * 255
            if len(stepactr) == 0:
                stepact = stepactl
            elif len(stepactl) == 0:
                stepact = stepactr
            else:
                stepact = np.concatenate((stepactr,stepactl),axis=1)
            trials.append(stepact)
            if len(stepact) > 0:
                plt.plot(time,stepact,'k',alpha=0.2)
            plt.ylim(0,0.25)
            plt.xlabel('time (s)')
            plt.ylabel('step activity (A.U.)')
            fname = str.format("{0}_{1}_centerstepping.png",subject,protocol)
            fpath = os.path.join(fbase,fname)
            plt.savefig(fpath)
            plt.close(fig)
            
    return trials
#    bigaverage = np.average(alltrials,axis=1)
#    bigsem = sp.stats.sem(alltrials,axis=1)
#    fig = plt.figure()
#    plt.fill_between(time,
#                     bigaverage-bigsem,
#                     bigaverage+bigsem,
#                     alpha=0.5)
#    plt.plot(time,bigaverage,'k')
#    plt.xlabel('time (s)')
#    plt.ylabel('step activity (A.U.)')
#    fname = str.format("bigaverage.png",subject,protocol)
#    fpath = os.path.join(path,fname)
#    plt.savefig(fpath)
#    plt.close(fig)
        
def __getclips__(act,cr,info,rowidx=slice(None)):
    features = []
    moviepath = activitymovies.getmoviepath(info)
    for (subject,session),group in cr.groupby(level=['subject','session']):
        steps = activitytables.stepfeature(act,group,4,3).iloc[rowidx,:]
        steps['subject'] = subject
        steps['session'] = session
        steps.reset_index(inplace=True)
        steps.set_index(['subject','session'],inplace=True)
        features.append(steps[['frame','side']].join(moviepath))
    return pd.concat(features)
    
def __processclips__(clips,xcrop=None,ycrop=None):
    for index,clip in clips:
        frames = activitymovies.framesiterable(clip.path,
                                               clip.frame-120,
                                               clip.frame+600)
        if clip.side == 'rightwards':
            frames = (cv2.flip(frame,1) for frame in frames)
        if xcrop is not None or ycrop is not None:
            xcrop = xcrop if xcrop is not None else slice(None)
            ycrop = ycrop if ycrop is not None else slice(None)
            frames = (frame[ycrop,xcrop] for frame in frames)
        yield frames
        
def __tileclips__(frames,width,height):
    for frame in frames:
        yield imgproc.tile(frame,width,height)[0]
        
def __transposeclips__(frames):
    for frame in frames:
        yield frame.T
        
def __resizeclips__(frames,dsize=None):
    for frame in frames:
        if dsize is not None:
            frame = cv2.resize(frame,dsize)
        yield frame
        
def __ensurecolor__(frames):
    for frame in frames:
        if frame.ndim < 3:
            frame = cv2.cvtColor(frame,cv2.cv.CV_GRAY2BGR)
        yield frame
        
def __savetiledclips__(act,cr,info,path,nclips=3):
    if not os.path.exists(path):
        os.makedirs(path)
        
    clips = __getclips__(act,cr,info,rowidx=slice(nclips))
    for subject,crossings in clips.groupby(level=['subject']):
#        fpath = os.path.join(path,subject)
#        if not os.path.exists(fpath):
#            os.makedirs(fpath)
        vidclips = __processclips__(crossings.iterrows(),ycrop=slice(320,-1))
        frames = __tileclips__(it.izip(*vidclips),1,nclips)
        fname = str.format("{0}_manipulations.avi",subject)
        vidpath = os.path.join(path,fname)
        activitymovies.savemovie(frames,vidpath,frames_per_second)
        
def __saveselectedtiledclips__(clips,info,path,suffix='.avi'):
    if not os.path.exists(path):
        os.makedirs(path)    
    
    moviepath = activitymovies.getmoviepath(info)
    for ((subject,session),group),indices in it.izip(info.groupby(level=['subject',
                                                                        'session']),
                                                     clips):
        crossings = pd.DataFrame(indices)
        crossings['path'] = moviepath.loc[(subject,session)]
        vidclips = __processclips__(crossings.iterrows(),ycrop=slice(320,-1))
        frames = __tileclips__(it.izip(*vidclips),1,len(crossings))
        fname = str.format("{0}"+suffix,subject)
        vidpath = os.path.join(path,fname)
        activitymovies.savemovie(frames,vidpath,frames_per_second)
        
def __getframes__(cr,info):
    movies = activitymovies.getmovies(info)
    for key,group in cr.groupby(level=['subject','session']):
        movie = movies.loc[key][0]
        for frametime in group:
            if pd.isnull(frametime):
                continue
            yield movie.frame(movie.frameindex(frametime))

def figure1m(clips,info,path):
    __saveselectedtiledclips__(clips,info,path,'_firststeps.avi')

def figure2a(clips,info,path):
    __saveselectedtiledclips__(clips,info,path,'_manipulation.avi')
    
def figure2a2(act,cr,info,path):
    features = []
    cr = cr[cr.stepstate3 == False]
    for (subject,session),group in cr.groupby(level=['subject','session']):
        steps = activitytables.stepcrossings(act,group,4,3).iloc[0:1,:]
        features.append(steps)
    return pd.concat(features)
        
def figure2b(act,cr,info,path):
    cr = cr[cr.stepstate3 == False]
    __savetiledclips__(act,cr,info,path,nclips=3)
    
def figure2b2(cr,info,path):
    cr = cr[cr.stepstate3 == False]
    moviepath = activitymovies.getwhiskermoviepath(info)
    timepath = activitymovies.getwhiskertimepath(info)
    for (subject,session),group in cr.groupby(level=['subject','session']):
        print str.format("Processing {0}...", subject)
        fname = str.format("{0}_manipulation.avi",subject)
        fpath = os.path.join(path,fname)
        crosstime = group.ix[0].crosstime
        movie = video.video(moviepath[subject,session],timepath[subject,session])
        alignframe = movie.frameindex(crosstime)
        frames = movie.movie(alignframe-240,alignframe+480)
        activitymovies.savemovie(frames,fpath,60,isColor=True)
    
def __colortrials__(frames,trialcolors):
    height = 25
    margin = 25
    cursoredge = 5
    colorbar = None
    colors = np.array([np.array(mpl.colors.colorConverter.to_rgb(color))*255
                      for color in trialcolors.color.values],dtype=np.uint8)
    colors = colors.reshape((1,len(trialcolors),3))
    colors = np.tile(colors,(height,1,1))
    
    for i,frame in enumerate(frames):
        if colorbar is None:
            width = frame.shape[1] - margin * 2
            cursortop = margin - cursoredge
            cursorbottom = margin + height + cursoredge
            colorbar = sp.misc.imresize(colors,(height,width,3))[:,:,::-1]
        frame = cv2.cvtColor(frame,cv2.cv.CV_GRAY2BGR)
        frame[margin:margin+height,margin:margin+width,:] = colorbar
        cursorpos = margin + width * i / len(trialcolors)
        cursorpt1 = (cursorpos,cursortop)
        cursorpt2 = (cursorpos,cursorbottom)
        cv2.line(frame,cursorpt1,cursorpt2,(0,0,0),3)
        cv2.line(frame,cursorpt1,cursorpt2,(255,255,255),1)
        yield frame
    
def figure2c(cr,info,path,suffix='.avi'):
    if not os.path.exists(path):
        os.makedirs(path)
    
    crinfo = cr.join(info)
    leftcross = crinfo[(cr.side == 'leftwards') & ~cr.crosstime.isnull()]
    for subject,group in leftcross.groupby(level=['subject']):
        print str.format("Processing {0}...",subject)
        fname = str.format("{0}"+suffix,subject)
        vidpath = os.path.join(path,fname)
        colors = getprotocolcolors(group)
        sinfo = info.xs(subject,level='subject',drop_level=False)
        frames = __getframes__(group.crosstime,sinfo)
        frames = __colortrials__(frames,colors)
        activitymovies.savemovie(frames,vidpath,30)
        
def figure2c2(cr,info,path):
    if not os.path.exists(path):
        os.makedirs(path)
    
    crinfo = cr.join(info)
    leftcross = crinfo[(cr.side == 'leftwards') & ~cr.crosstime.isnull()]
    fname = str.format("lifetimeleft.csv")
    csvpath = os.path.join(path,fname)
    leftcross[['trial',
               'protocol',
               'stepstate1',
               'stepstate2',
               'stepstate3',
               'stepstate4',
               'stepstate5',
               'stepstate6']].to_csv(csvpath)
        
def figure2e(act,cr,rr,info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    features = []
    cr = cr[cr.stepstate3 == False]
    for (subject,session),group in cr.groupby(level=['subject','session']):
        #step = activitytables.stepframeindices(act,group,4,3)
        step = activitytables.stepfeature(act,group,4,3).iloc[0:1,:]
        step['subject'] = subject
        step['session'] = session
        step.reset_index(inplace=True)
        step.set_index(['subject','session'],inplace=True)
        steprr = step.join(rr,rsuffix='reward')
        timetoreward = steprr.timereward - steprr.time
        timetoreward = timetoreward[timetoreward > 0]
        features.append((subject,timetoreward.min()))
        
    fig = plt.figure()        
    n = [(m[1].values[0]/np.timedelta64(1,'s') if m[1] is not np.nan else np.nan,
          m[0],5) for m in features]
    data = pd.DataFrame(n,columns=['timetoreward','subject','session'])
    data.set_index(['subject','session'],inplace=True)
    result = activitytables.groupbylesionvolumes(data,info)
    
    ncontrols = sum((1 for m in result.index.labels[1] if m == 0))
    nlesions = sum((1 for m in result.index.labels[1] if m == 1))
    clabels = ['C' + chr(ord('a') + i) for i in range(ncontrols)]
    llabels = ['L' + chr(ord('a') + i) for i in range(nlesions)]
    
    plt.bar(range(len(result)),result.timetoreward,color=['b']*11 + ['r']*11)
    plt.xlim(-1,len(result) + 1)
    plt.xticks(np.arange(len(result)) + 0.4,clabels+llabels)
    plt.xlabel('subject')
    plt.ylabel('time to reward (s)')
    plt.title('time to first reward after manipulation')
    p1 = plt.Rectangle((0, 0), 1, 1, fc="b")
    p2 = plt.Rectangle((0, 0), 1, 1, fc="r")
    plt.legend([p1,p2],['control', 'lesion'])
    
    fname = str.format("manipulation_first_reward_time.png",subject)
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
    
def __getmanipulationframes__(act,info):
    ethopath = activitymovies.getrelativepath(info,'Analysis\ethogram.csv')
    frames = []
    side = []
    keys = []
    for key,item in ethopath.iteritems():
        keys.append(key)
        side.append('leftwards')
        if os.path.exists(item):
            ethogram = pd.read_csv(item,' ',header=None,names=['event','time'])
            contact = pd.to_datetime(ethogram.time[ethogram.event == 'Contact'])[0]
            frames.append(act.frame[contact])
        else:
            frames.append(0)
    return pd.DataFrame({'frame':frames,'side':side},
                        index=pd.MultiIndex.from_tuples(keys,names=['subject','session']))
                        
def figure2a3(act,info,path):
    if not os.path.exists(path):
        os.makedirs(path)    
    
    mframes = __getmanipulationframes__(act,info)
    mframes = mframes.join(info)
    mframes = mframes[mframes.frame != 0]
    mframes = mframes.query('subject not in ["JPAK_26","JPAK_27","JPAK_28","JPAK_29"]')
    mframes = mframes.join(activitymovies.getmoviepath(mframes))
    mframes = activitytables.groupbylesionvolumes(mframes[['path','frame','side']],mframes)
    mframes.reset_index()
    
    vidclips = __processclips__(mframes.iterrows(),ycrop=slice(320,-1))
    vidclips = [__transposeclips__(clip) for clip in vidclips]
    frames = __tileclips__(it.izip(*vidclips),len(mframes)/2,2)
    frames = __transposeclips__(frames)
    frames = __resizeclips__(frames,dsize=(1280,896))
    fname = str.format("manipulations_big_lesion.avi")
    vidpath = os.path.join(path,fname)
    activitymovies.savemovie(frames,vidpath,frames_per_second)
    
def figure2a4(act,info,path):
    if not os.path.exists(path):
        os.makedirs(path)    
    
    mframes = __getmanipulationframes__(act,info)
    mframes = mframes.join(info)
    mframes = mframes[mframes.frame != 0]
    mframes = mframes.join(activitymovies.getmoviepath(mframes))
    mframes.reset_index(inplace=True)
    
    vidclips = __processclips__(mframes.iterrows())
    frames = next(vidclips)
    fname = str.format("manipulation.avi")
    vidpath = os.path.join(path,fname)
    activitymovies.savemovie(frames,vidpath,frames_per_second)