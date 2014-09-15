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
from preprocess import storepath, labelpath, frontactivity_key, rewards_key
from preprocess import max_width_cm, width_pixel_to_cm
from preprocess import rail_start_pixels, rail_stop_pixels

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
    
def read_crossings(path):
    activity = read_activity(path)
    crosses = crossings(activity)
    labelh5path = labelpath(path)
    if os.path.exists(labelh5path):
        crosses.label = pd.read_hdf(labelh5path, 'label')
    return activity,crosses
    
def read_crossings_group(folders):
    crossings = []
    for path in folders:
        activity,cr = read_crossings(path)
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
    
def read_crossings_subjects(folders, days=None):
    subjects = []
    for path in folders:
        crossings = read_crossings_group(sessions.findsessions(path, days))
        crossings['subject'] = os.path.split(path)[1]
        labelsfile = os.path.join(path, 'labels.csv')
        appendlabels(crossings,labelsfile)
        subjects.append(crossings)
    return pd.concat(subjects)
    
def slowdown(crossings):
    return pd.DataFrame(
    [stats.linregress(crossings.entryspeed,crossings.exitspeed)],
     columns=['slope','intercept','r-value','p-value','stderr'])

def crossings(activity):
    # Generate trajectories and crossings
    center = max_width_cm / 2.0
    cropleft = rail_start_pixels * width_pixel_to_cm
    cropright = rail_stop_pixels * width_pixel_to_cm
    xhead = activity.xhead
    sparsetraj = np.ma.clump_unmasked(np.ma.masked_invalid(activity.xhead))
    crossings = [s for s in sparsetraj
    if xhead[s.start] > center and xhead[s.stop-1] < center
    or xhead[s.start] < center and xhead[s.stop-1] > center]
    crossings = cropcrossings(xhead,crossings,[cropleft,cropright])
    
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
                      duration,
                      maxheight,
                      maxspeed,
                      entryspeed,
                      exitspeed],
                      axis=1)
    