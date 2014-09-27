# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 11:42:00 2014

@author: Gonçalo
"""

import os
import pltutils
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import activitytables
from preprocess import labelpath
from collectionselector import CollectionSelector

def sessionmetric(data,yerr=None,connect=True,ax=None):
    if ax is None:
        ax = plt.gca()
    xticks = []
    groupcount = 0

    groupcenters = []
    groupmeans = []
    grouperr = []
    for session,subjectgroups in data.groupby(level=0):
        nsubjects = len(subjectgroups)
        step = 0.5 / nsubjects
        offset = -0.25
        ax.set_color_cycle(None)
        groupedsubjects = subjectgroups.groupby(level=1)
        groupcount = len(groupedsubjects)
        for i,(groupname,subjects) in enumerate(groupedsubjects):
            x = session + offset + step * np.arange(len(subjects))
            _,caps,_ = plt.errorbar(x,subjects.icol(0),subjects.icol(1),
                                      fmt=None,label=groupname,
                                      zorder=100,capthick=1,alpha=0.4)
            for cap in caps:
                cap.remove()

            if i >= len(groupcenters):
                groupcenters.append([])
                groupmeans.append([])
                grouperr.append([])
            groupcenters[i].append((x[-1] + x[0]) / 2.0)
            groupmeans[i].append(subjects.icol(0).mean())
            grouperr[i].append(subjects.icol(0).std())
            offset += step * len(subjects)
        xticks.append(session)
    
    ax.set_color_cycle(None)
    for center,mean,err in zip(groupcenters,groupmeans,grouperr):
        plt.errorbar(center,mean,err,
                     fmt='--' if connect else None,ecolor='k',
                     linewidth=2,capthick=2,markersize=0)
                     
    if not connect:
        ylims = ax.get_ylim()
        for left,right in zip(xticks,xticks[1:]):
            boundary = (left + right) / 2.0
            ax.plot((boundary,boundary),ylims,'k--')
        ax.set_ylim(ylims)
        
    ax.set_xticks(xticks)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:groupcount],labels[:groupcount])
    ax.set_xlabel(data.index.names[0])
        
def fpshist(activity,ax=None):
    if ax is None:
        ax = plt.gca()
    (1.0 / activity.timedelta).hist(ax=ax,bins=100,normed=True)
    ax.set_xlabel('fps')
    ax.set_title('frame rate')
    
def trajectoryplot(activity,crossings,ax=None,style='k',alpha=1):
    if ax is None:
        ax = plt.gca()
    for s in crossings.slices:
        ax.plot(activity.xhead[s],activity.yhead[s],style,alpha=alpha)
    ax.set_title('trajectories')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('y (cm)')
    
def featuresummary(crossings,ax=None,onselect=None):
    if ax is None:
        ax = plt.gca()
    pts = ax.scatter(crossings.duration,crossings.yhead_max,
               s=10,marker='D',facecolors='b',edgecolors='none')
    selector = CollectionSelector(ax,pts,color_other='r',
                                  onselection=onselect)
    ax.set_title('trajectory features')
    ax.set_xlabel('duration (s)')
    ax.set_ylabel('max height (cm)')
    return selector
    
def slowdownsummary(crossings,ax=None,regress=True):
    if ax is None:
        ax = plt.gca()
    entryspeed = crossings.entryspeed
    exitspeed = crossings.exitspeed
    ax.plot(entryspeed,exitspeed,'.')
    if regress:
        pltutils.regressionline(entryspeed,exitspeed,ax,color='k')
    ax.set_title('slowdown')
    ax.set_xlabel('entry speed (cm / s)')
    ax.set_ylabel('exit speed (cm / s)')
    
def rewardrate(rewards,ax=None):
    if ax is None:
        ax = plt.gca()
    intervals = rewards.time.diff() / np.timedelta64(1,'m')
    ax.plot(1.0 / intervals)
    ax.set_title('reward rate')
    ax.set_xlabel('trials')
    ax.set_ylabel('r.p.m')
    
def clearhandles(handles):
    while len(handles) > 0:
        handle = handles.pop()
        if np.iterable(handle):
            for l in handle:
                l.remove()
                del l
        del handle
        
def clearcollection(handles):
    while len(handles) > 0:
        handle = handles.pop()
        handle.remove()
        del handle

def sessionsummary(path):
    labelh5path = labelpath(path)
    activity = activitytables.read_activity(path)
    crossings = activitytables.read_crossings(path,activity)
    rewards = activitytables.read_rewards(path)
    
    selected = []
    def onselect(ind):
        selector.ind[:] = ind
        selector.updateselection()
        clearhandles(selected)
        if len(ind) <= 0:
            return
        
        for s in crossings.slices[ind]:
            h = axs[0,1].plot(activity.xhead[s],activity.yhead[s],'r')
            selected.append(h)
            
    markers = []
    def updateplots():
        onselect([])
        clearcollection(markers)
        valid = crossings.label == 'valid'
        
        axs[0,1].clear()
        trajectoryplot(activity,crossings[valid],axs[0,1],alpha=0.2)
        
        axs[1,2].clear()
        slowdownsummary(crossings[valid],axs[1,2])
        
        invalid = crossings.label == 'invalid'
        if invalid.any():
            rows = crossings[invalid]
            pts = axs[0,2].scatter(rows.duration,rows.yhead_max,
                           s=20,marker='x',facecolors='none',edgecolors='r')
            markers.append(pts)
        fig.canvas.draw_idle()
            
    def onkeypress(evt):
        label = None
        if evt.key == 'q':
            crossings.label.to_hdf(labelh5path, 'label')
        if evt.key == 'r':
            label = 'invalid'
        if evt.key == 'v':
            label = 'valid'
        if label != None:
            crossings.label[selector.ind] = label
            updateplots()
    
    fig, axs = plt.subplots(3,3)
    fpshist(activity,axs[0,0])
    selector = featuresummary(crossings,axs[0,2],onselect)
    updateplots()
    rewardrate(rewards,axs[1,0])
    fig.canvas.mpl_connect('key_press_event',onkeypress)
    
    plt.tight_layout()
    return activity,crossings,rewards,selector