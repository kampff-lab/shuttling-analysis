# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 05:22:49 2014

@author: Gonçalo
"""

import os
import sessions
import numpy as np
import pandas as pd
import scipy.stats as stats
from preprocess import storepath, labelpath
from preprocess import frontactivity_key, rewards_key, info_key
from preprocess import max_width_cm, width_pixel_to_cm
from preprocess import rail_start_pixels, rail_stop_pixels

def groupbylesionvolumes(data,info):
    lesionvolume = info['lesionleft'] + info['lesionright']
    lesionvolume.name = 'lesionvolume'
    g = pd.concat([data,lesionvolume,info['cagemate']],axis=1)
    lesionorder = g[g['lesionvolume'] > 0].sort('lesionvolume',ascending=False)
    controls = lesionorder.groupby('cagemate',sort=False).median().index
    controlorder = g.reset_index().set_index('subject').ix[controls]
    controlorder.set_index('session',append=True,inplace=True)
    result = pd.concat([controlorder,lesionorder])
    result['lesion'] = ['lesion' if v > 0 else 'control'
                        for v in result['lesionvolume']]
    result.reset_index(inplace=True)
    result.sort(['session','lesion'],inplace=True)
    result.set_index(['session','lesion','subject'],inplace=True)
    result.drop(['lesionvolume','cagemate'],axis=1,inplace=True)
    return result

def geomediancost(median,xs):
    return np.linalg.norm(xs-median,axis=1).sum()
    
def mad(xs):
    median = xs.median()
    return (xs - median).abs().median()

def cropcrossings(x,slices,crop):
    def test_slice(s):
        return (x[s] > crop[0]) & (x[s] < crop[1])
    
    def crop_slice(s):
        valid_indices = np.nonzero(test_slice(s))[0]
        min_index = np.min(valid_indices)
        max_index = np.max(valid_indices)
        return slice(s.start+min_index,s.start+max_index+1)
    return [crop_slice(s) for s in slices if np.any(test_slice(s))]
    
def read_activity(path):
    return pd.read_hdf(storepath(path), frontactivity_key)
    
def read_rewards(path):
    return pd.read_hdf(storepath(path), rewards_key)
    
def read_crossings(path, activity):
    crosses = crossings(activity)
    labelh5path = labelpath(path)
    if os.path.exists(labelh5path):
        crosses.label = pd.read_hdf(labelh5path, 'label')
    return crosses
    
def read_crossings_group(folders):
    crossings = []
    for path in folders:
        activity = read_activity(path)
        cr = read_crossings(path, activity)
        cr['session'] = os.path.split(path)[1]
        crossings.append(cr)
    return pd.concat(crossings)
    
def appendlabels(data,labelspath):
    if os.path.exists(labelspath):
        with open(labelspath) as f:
            for line in f:
                label,value = line.split(':')
                try:
                    value = float(value)
                except ValueError:
                    value = value
                data[label] = value
    
def read_subjects(folders, days=None,
                  key=frontactivity_key, selector=None):
    if isinstance(folders, str):
        folders = [folders]
                      
    subjects = []
    for path in folders:
        subject = read_sessions(sessions.findsessions(path, days),
                                key,selector)
        subjects.append(subject)
    return pd.concat(subjects)
    
def read_sessions(folders, key=frontactivity_key, selector=None):
    if isinstance(folders, str):
        folders = [folders]
    
    sessions = []
    for path in folders:
        session = pd.read_hdf(storepath(path), key)
        if selector is not None:
            session = selector(session)

        if key != info_key:
            info = pd.read_hdf(storepath(path), info_key)
            info.reset_index(inplace=True)
            keys = [n for n in session.index.names if n is not None]
            session.reset_index(inplace=True)
            session['subject'] = info.subject.iloc[0]
            session['session'] = info.session.iloc[0]
            session.set_index(['subject', 'session'], inplace=True)
            session.set_index(keys, append=True, inplace=True)
        sessions.append(session)
    return pd.concat(sessions)
    
def slowdown(crossings):
    return pd.DataFrame(
    [stats.linregress(crossings.entryspeed,crossings.exitspeed)],
     columns=['slope','intercept','r-value','p-value','stderr'])

def crossings(activity,midcross=True,crop=True):
    # Generate trajectories and crossings
    center = max_width_cm / 2.0
    cropleft = rail_start_pixels * width_pixel_to_cm
    cropright = rail_stop_pixels * width_pixel_to_cm
    xhead = activity.xhead
    crossings = np.ma.clump_unmasked(np.ma.masked_invalid(activity.xhead))
    if midcross:
        crossings = [s for s in crossings
        if xhead[s.start] > center and xhead[s.stop-1] < center
        or xhead[s.start] < center and xhead[s.stop-1] > center]
    if crop:
        crossings = cropcrossings(xhead,crossings,[cropleft,cropright])
        
    # Trial info
    trialinfo = pd.DataFrame([activity.iloc[s.start,0:7] for s in crossings])
    trialinfo.reset_index(inplace=True,drop=True)
    
    # Generate crossing features
    time = activity.index
    label = pd.DataFrame(['valid' for s in crossings],columns=['label'])
    maxheight = pd.DataFrame([activity.yhead[s].max() for s in crossings],
                              columns=['yhead_max'])
                              
    duration = pd.DataFrame([(time[s.stop]-time[s.start]).total_seconds()
    for s in crossings],
    columns=['duration'])
    maxspeed = pd.DataFrame([activity.xhead_speed[s].abs().max()
    for s in crossings],
    columns=['xhead_speed_max'])
    
    # Slowdown
    xspeed = activity.xhead_speed
    midbounds = np.array([425,850]) * width_pixel_to_cm
    midpoints = [xhead[s] > midbounds[0]
    if xhead[s.stop] > xhead[s.start]
    else xhead[s] < midbounds[1]
    for s in crossings]
    entryspeed = pd.DataFrame([np.abs(xspeed[s][~v].mean())
    for s,v in zip(crossings,midpoints)],columns=['entryspeed'])
    exitspeed = pd.DataFrame([np.abs(xspeed[s][v].mean())
    for s,v in zip(crossings,midpoints)],columns=['exitspeed'])
    
    crossings = pd.DataFrame(crossings,columns=['slices'])
    return pd.concat([crossings,
                      label,
                      trialinfo,
                      duration,
                      maxheight,
                      maxspeed,
                      entryspeed,
                      exitspeed],
                      axis=1)
    