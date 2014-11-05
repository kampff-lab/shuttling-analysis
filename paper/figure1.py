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
import pandas as pd
import itertools as it
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import activitytables
import activityplots
import activitymovies
from preprocess import labelpath, rail_start_cm, rail_stop_cm
from preprocess import max_width_cm, max_height_cm
from preprocess import stepcenter_cm, stepcenter_pixels
from collectionselector import CollectionSelector
from pandas.tools.plotting import scatter_matrix

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

heightcutoff = 20.42
cropstart = str(rail_start_cm)
cropstop = str(rail_stop_cm)
heightfilter = str.format('yhead_max > 0 and yhead_max < {0}',heightcutoff)
positionfilter = str.format('xhead_min >= {0} and xhead_max <= {1}',
                            cropstart, cropstop)
speedfilter = 'xhead_speed_25 > 0'
ballisticquery = str.format('{0} and {1} and {2}',
                   heightfilter,positionfilter,speedfilter)

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
    
    fig = plt.figure()
    activityplots.sessionmetric(rrgdata)
    plt.ylabel('time between rewards (s)')
    plt.title('performance curve')
    fname = 'performance_curve.png'
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
    plt.xlim(0,25)
    plt.ylim(0,25)
    plt.xlabel('duration (s)')
    plt.ylabel('max height (cm)')
    plt.title(title)
    plt.legend()
    fpath = os.path.join(path,fname)
    plt.savefig(fpath)
    plt.close(fig)
    
def figure1c0(cr,path,alpha=1,
              fname='all_subjects_duration_maxheight.png'):
    groups = cr[cr.trial > 0]
    __poolfeaturecomparison__([('crossings',groups)],path,['b'],None,
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
        
def getballistictrials(cr):
    return cr.query(ballisticquery)
    
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
    activityplots.sessionmetric(d,ax=ax,colorcycle=colorcycle,connect=False)
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
        
        days = group.index.levels[1][group.index.labels[1]]
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
        
def figure1k3(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject'])
    for subject,sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        
        stepframes = []
        stinfo = sinfo[sinfo.protocol == 'stable']
        for key,group in stinfo.groupby(level=['session']):
            stact = activitytables.read_subjects(subjectpath,days=[key])
            stcr = activitytables.read_subjects(subjectpath,days=[key],
                                                selector = activitytables.crossings)
            stepframes += activitytables.stepframes(stact,stcr,group,4,3,
                                                    subtractBackground=True)
        stepframes = [cv2.threshold(f, 5, 255, cv2.cv.CV_THRESH_BINARY)[1]
                      for f in stepframes]
        stavg = imgproc.average(stepframes,1)
        
        stepframes = []
        uinfo = sinfo[sinfo.protocol != 'stable']
        for key,group in uinfo.groupby(level=['session']):
            uact = activitytables.read_subjects(subjectpath,days=[key])
            ucr = activitytables.read_subjects(subjectpath,days=[key],
                                                selector = activitytables.crossings)
            stepframes += activitytables.stepframes(uact,ucr,group,4,3,
                                                    subtractBackground=True)
        stepframes = [cv2.threshold(f, 5, 255, cv2.cv.CV_THRESH_BINARY)[1]
                      for f in stepframes]
        uavg = imgproc.average(stepframes,1)
        
        avg = cv2.merge((uavg,stavg,np.zeros(stavg.shape,dtype=stavg.dtype)))
        avg = avg.astype(np.uint8)
        avg = cv2.convertScaleAbs(avg,alpha=1.4,beta=0.0)
        plt.imshow(avg)
        plt.title(str.format('{0}',subject))
        fname = str.format("{0}_posture_stable_unstable.png", subject)
        fpath = os.path.join(path,fname)
        plt.axis("off")
        plt.savefig(fpath)
        plt.close(fig)
        
def figure1l(info,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    sessions = info.groupby(level=['subject'])
    for subject,sinfo in sessions:
        fig = plt.figure()
        subjectpath = os.path.join(activitymovies.datafolder,subject)
        days = sinfo.index.levels[1][sinfo.index.labels[1]]
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
        activityplots.scatterhist(stfeatures.xhead,stfeatures.yhead,color='b',
                                  bins=bins,axes=axes,xlim=xlim,ylim=ylim,
                                  histalpha=alpha)
        
        uact = act[~act.stepstate3]
        ucr = cr[~cr.stepstate3]
        ufeatures = activitytables.stepfeature(uact,ucr,4,3)
        leftwards = ufeatures.side == 'leftwards'
        ufeatures.xhead[leftwards] = max_width_cm - ufeatures.xhead[leftwards]
        ufeatures.xhead -= stepoffset
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
        
def figure2e(act,cr,rr,path):
    if not os.path.exists(path):
        os.makedirs(path)
        
    features = []
    cr = cr[cr.stepstate3 == False]
    for subject,session in cr.groupby(level=['subject']):
        step = activitytables.stepfeature(act,session,4,3).iloc[0:1,:]
        step = step.reset_index('time')
        steprr = step.join(rr,rsuffix='reward')
        timetoreward = steprr.timereward - steprr.time
        timetoreward = timetoreward[timetoreward > 0]
        features.append(timetoreward.min())
    return features