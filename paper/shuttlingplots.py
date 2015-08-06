# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:01:47 2015

@author: Gonçalo
"""

import cv2
import video
import imgproc
import datapath
import activitytables
import activityplots
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from activitytables import rail_start_cm, rail_stop_cm
from activitytables import steprois_cm, steprois_crop
from preprocess import width_pixel_to_cm, height_pixel_to_cm
from preprocess import max_height_cm, center_cm
from preprocess import rail_height_pixels, steprois_pixels
from roiset import RoiSet

_stepoffset_ = steprois_cm.center[3][1]
_splitprotocols_ = ['stabletocenterfree',
                    'centerfreetostable',
                    'randomizedcenterfree_day1']
                    
_groupcolors_ = ['b','m','r','k']

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
    
def activitysummary(info,rr,lpoke,rpoke,vcr,cr,ax=None):
    pooled = None
    sessions = info.groupby(level=['subject','session'])
    for key,sinfo in sessions:
        try:
            srr = rr.ix[key,:].set_index('index')
        except KeyError:
            continue
        slpoke = lpoke.ix[key,:].set_index('index')
        srpoke = rpoke.ix[key,:].set_index('index')
        svcr = vcr.ix[key,:].set_index('index')
        scr = cr.ix[key,:].set_index('index')
        
        if len(srr) > 1:
            trialact = activitytables.trialactivity(srr,
                                                    slpoke,srpoke,
                                                    scr,svcr).sum()
            if pooled is None:
                pooled = trialact
            else:
                pooled += trialact

    pooled.ix[:-1].plot(kind='pie',ax=ax)
    
def averagetrajectory(cract,cr,column='yhead',baseline=None,
                      color='b',ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    selector = lambda x:x[column]
    xpoints = np.linspace(rail_start_cm,rail_stop_cm,100)
    for subject,subcr in cr.groupby(level=['subject']):
        ypoints = activitytables.spatialinterp(xpoints,cract,subcr,selector)
        if baseline is not None:
            ypoints -= np.nanmean(ypoints[:,baseline])
        ymean = np.mean(ypoints,axis=0)
        yerr = stats.sem(ypoints,axis=0)
        ax.fill_between(xpoints,ymean-yerr,ymean+yerr,color=color,alpha=0.1)
    ax.set_xlabel('x (cm)')
    ax.set_xlim(5,45)
    
def createspaceaxis():
    return np.linspace(rail_start_cm,rail_stop_cm,72)-_stepoffset_
    
def averagetimeseries(cract,column=None,baseline=None,
                      color='b',ax=None,**kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    xpoints = createspaceaxis()
    ymean,yerr = activitytables.spatialaverage(xpoints,cract,column,baseline)
    activityplots.boundedcurve(xpoints,ymean,yerr,color=color,ax=ax,**kwargs)
    ax.set_xlabel('x (cm)')
    ax.set_xlim(-15,25)
        
def averagetimetrajectory(cract,color='b',ax=None,**kwargs):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    
    for key,subcr in cract.groupby(level=['subject','session','crossing']):
        time = (subcr.time - subcr.time[0]) / np.timedelta64(1,'s')
        ax.plot(time,subcr.xhead,subcr.yhead,color=color,**kwargs)
    ax.set_ylabel('x (cm)')
    ax.set_xlabel('time (s)')
    ax.set_zlabel('y (cm)')
    
def skipprobability(cr,ax=None):
    cr = cr.copy(deep=True)
    skip = cr.steptime3.isnull() & cr.steptime4.isnull()
    cr['skip'] = skip
    cr.reset_index(inplace=True)
    grouped = cr.groupby(['protocol','subject'],sort=False)['skip']
    result = pd.concat([grouped.sum(),grouped.count()],axis=1)
    result.columns = ['skip','total']
    result['frequency'] = result.skip / result.total
    return result
    
def skipprobability_subject(cr,info,ax=None):
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
    
def proxylegend(colors,labels,ax=None,**kwargs):
    if ax is None:
        ax = plt.gca()
    handles = [plt.Rectangle((0,0),1,1,color=color) for color in colors]
    ax.legend(handles,labels,**kwargs)

def _averageposture_(cract,info,cr,cropsize=(300,300)):

    stepframes = []
    for key,scr in cr.groupby(level=['subject','session']):
        sinfo = info.loc[[key],:]
        stepframes += activitytables.stepframes(cract,scr,sinfo,4,3,
                                                cropsize=cropsize,
                                                subtractBackground=True)
    stepframes = [cv2.threshold(f, 5, 255, cv2.cv.CV_THRESH_BINARY)[1]
                  for f in stepframes]
    return imgproc.average(stepframes,1)

def averageposturecomparison(cract,info,cr1,cr2,cr3=None,
                             cropsize=(300,300),ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    avg1 = _averageposture_(cract,info,cr1,cropsize)
    avg2 = _averageposture_(cract,info,cr2,cropsize)
    if cr3 is not None:
        avg3 = _averageposture_(cract,info,cr3,cropsize)
    else:
        avg3 = np.zeros(cropsize,dtype=np.float32)
        
    avg = cv2.merge((avg1,avg2,avg3))
    avg = avg.astype(np.uint8)
    avg = cv2.convertScaleAbs(avg,alpha=1.4,beta=0.0)
    cv2.flip(avg,1,avg)
    ax.imshow(avg)
    ax.set_axis_off()
    
def scatterhistaxes():
    plt.figure()
    axScatter = plt.subplot2grid((3,3),(1,0),rowspan=2,colspan=2)
    axHistx = plt.subplot2grid((3,3),(0,0),colspan=2)
    axHisty = plt.subplot2grid((3,3),(1,2),rowspan=2)
    return (axScatter,axHistx,axHisty)

def posturehistogram(steps,rangex=None,rangey=None,
                     color='b',histalpha = 0.75,scatteralpha = 0.4,
                     axes=None):
    if axes is None:
        axes = scatterhistaxes()

    if rangex is None:
        rangex = (steps.xhead.min(),steps.xhead.max())
        
    if rangey is None:
        rangey = (steps.yhead.min(),steps.yhead.max())
        
    xbinsize = 5 * width_pixel_to_cm
    ybinsize = 10 * height_pixel_to_cm
    xbins = np.arange(rangex[0],rangex[1]+xbinsize,xbinsize)
    ybins = np.arange(rangey[0],rangey[1]+ybinsize,ybinsize)
    xlim = (np.floor(rangex[0]),np.ceil(rangex[1]))
    ylim = (np.floor(rangey[0]),np.ceil(rangey[1]))
    activityplots.scatterhist(steps.xhead,steps.yhead,
                              xbins=xbins,ybins=ybins,
                              color=color,axes=axes,xlim=xlim,ylim=ylim,
                              histalpha=histalpha,alpha=scatteralpha)
    axScatter = axes[0]
    axScatter.set_xlabel('x (cm)')
    axScatter.set_ylabel('y (cm)')
    
def posturemean(steps,color='b',label=None,ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
        
    xhead = activitytables.flipleftwards(steps.xhead,steps.side)
    xmean = xhead.mean()
    ymean = steps.yhead.mean()
    xerr = xhead.sem()
    yerr = steps.yhead.sem()
    ax.scatter(xmean,ymean,color=color)
    ax.errorbar(xmean,ymean,xerr=xerr,yerr=yerr,ecolor=color)
    if label is not None:
        ax.annotate(label,xy=(xmean,ymean),textcoords='offset points')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('y (cm)')
    
def _cmtopixel_(x,y):
    x = (x / width_pixel_to_cm)
    y = ((max_height_cm - y) / height_pixel_to_cm) - rail_height_pixels
    return x,y
    
def _pixelcrop_(x,y,cropcenter,cropsize):
    x -= cropcenter[1] - cropsize[1] / 2
    y -= cropcenter[0] - cropsize[1] / 2
    return x,y
    
def _stepframes_(steps,info,cropsize=(300,300)):
    stepframes = []
    for key,scr in steps.groupby(level=['subject','session']):
        sinfo = info.loc[[key],:]
        stepframes += activitytables.roiframes(scr.frame,scr.side,sinfo,4,3,
                                               activitytables.cropstep,
                                               cropsize=cropsize,
                                               subtractBackground=True)
    return stepframes

def medianposture(steps,info,cropsize=(300,300),ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    xhead = activitytables.flipleftwards(steps.xhead,steps.side)
    median = steps[xhead == xhead.median()].iloc[-1,:]
    stepindex = 4 if median.side == 'leftwards' else 3
    stepcenter = steprois_crop.center[stepindex]
    info = info.ix[median.name[:2],:]
    videopath = datapath.relativepath(info,'front_video.avi')
    
    background = video.readsinglebackground(videopath,median.frame)
    background = cv2.cvtColor(background,cv2.cv.CV_GRAY2BGR)
    background *= 2.1
    
    frame = video.readsingleframe(videopath,median.frame,segmented=True)
    _,mask = cv2.threshold(frame,3,255,cv2.cv.CV_THRESH_BINARY)
    mask = mask.astype(np.bool)
    frame = cv2.cvtColor(frame,cv2.cv.CV_GRAY2BGR)
    frame *= 2.1
    
    frame[mask,...] += background[mask,...]
    fliprois = RoiSet(steprois_pixels.rois,flipxy=True)
    pts = np.array(fliprois.rois[stepindex])
    cv2.polylines(background,[pts],True,(0,0,255),2)
    background[mask,...] = frame[mask,...]
    frame = background
    
    frame = imgproc.croprect(stepcenter,cropsize,frame)
    ax.imshow(frame)
    x,y = _cmtopixel_(median.xhead,median.yhead)
    x,y = _pixelcrop_(x,y,stepcenter,cropsize)
    ax.scatter(x,y,color='r')
    ax.set_axis_off()
    
def _significance_(p):
    if p < 0.0001:
        return '****'
    elif p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    else:
        return 'ns'
    
def _conditionstats_(condition,column,names):
    data = condition.query(str.format('subject in {0}',list(names)))[column]
    return data, data.mean(), data.sem()

def conditioncomparison(column,groups,conditions,colors,ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
    
    baridx = 0
    control = None
    baroffset = len(conditions)+1
    for group in groups:
        gstats = [_conditionstats_(condition,column,group)
                  for condition in conditions]
        for i,((data,mean,yerr),color) in enumerate(zip(gstats,colors)):
            ax.bar(baridx+i,mean,color=color,yerr=yerr,ecolor='k')

        if control is None:
            control = gstats
        else:
            for i,(cdata,gdata) in enumerate(zip(control,gstats)):
                mean = gdata[1]
                offset = gdata[2] if mean >= 0 else -gdata[2]
                _,p = stats.ttest_ind(cdata[0],gdata[0])
                ax.annotate(_significance_(p),
                            (baridx+0.5+i,mean+offset),
                            ha='center',
                            va='bottom' if mean >= 0 else 'top')
        baridx += baroffset
    xticks = np.arange(len(conditions)/2.0,baroffset*len(groups),baroffset)
    ax.set_xticks(xticks)
    ax.set_ylabel('nose height (zscore)')

def groupcomparison(groups,colors,markers=None,facecolors=None,s=30,ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
        
    if markers is None:
        markers = ['o' for c in colors]
        
    if facecolors is None:
        facecolors = [c for c in colors]
    
    for i,(group,color,marker,facecolor) in enumerate(zip(groups,
                                                          colors,
                                                          markers,
                                                          facecolors)):
        mean = group.mean()
        yerr = group.sem()
        ax.scatter([i]*len(group),group,color=color,
                   s=s,marker=marker,facecolor=facecolor)
        ax.errorbar(i+0.2,mean,yerr=yerr,ecolor='k',fmt=None,
                    elinewidth=3,capthick=3,capsize=6)
    ax.set_xlim(-1,len(groups))

def barcomparison(data,color,left=0,by=None,level=None,column=None,ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca()
        
    if column is None:
        column = data.columns
    
    grouped = data.groupby(by=by,level=level,sort=False)
    if isinstance(color,str):
        color = [color] * len(grouped)

    width = 0.8
    for i,((key,group),c) in enumerate(zip(grouped,color)):
        group = group[column]
        mean = group.mean()
        yerr = group.sem()
        ax.bar(left+i,mean,yerr=yerr,
               color=c,ecolor='k',width=width,zorder=1,
               linewidth=1,error_kw={'elinewidth':2,'capthick':2,'capsize':4})
        ax.scatter([left+i+width/2]*len(group),group,s=15,
                   color=c,edgecolor='k',zorder=2)
    ax.set_xticks([left+i+width/2 for i in range(len(grouped))])
