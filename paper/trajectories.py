# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 16:12:45 2013

@author: gonca_000
"""

import os
import numpy as np

max_height_cm = 24.0
height_pixel_to_cm = max_height_cm / 680.0
width_pixel_to_cm = 50.0 / 1280.0
rail_height_pixels = 100
frames_per_second = 120.0

# stores tip trajectories from shuttling task
# * data rows are frames
# * data cols are [xleft,yleft,xright,yright]

class trajectories:
    def __init__(self, data, slices=None, **kwargs):
        self.data = data
        if slices is None:
            mask = kwargs.get('mask')
            if mask is None:
                mask = np.ma.masked_equal(data[:,0],-1)
            slices = np.ma.clump_unmasked(mask)
        self.slices = slices
        
    def tolist(self):
        return [self.data[s,:] for s in self.slices]
        
def scale(ts,sx=width_pixel_to_cm,sy=height_pixel_to_cm,by=rail_height_pixels,my=max_height_cm):
    scaled = [0,my,0,my] - (ts.data + [0,by,0,by]) * [-sx,sy,-sx,sy]
    return trajectories(scaled,ts.slices)
    
def crossings(ts,center=640):
    return trajectories(ts.data,[s for s in ts.slices if
    (ts.data[s.start,0] < center and ts.data[s.stop-1,0] > center) or
    (ts.data[s.start,0] > center and ts.data[s.stop-1,0] < center)])
    
def lengthfilter(ts,minlength=None,maxlength=None):
    return trajectories(ts.data,[s for s in ts.slices if
    s.stop-s.start >= minlength and (maxlength is None or s.stop-s.start <= maxlength)])
    
def crop(ts,crop=[200,1000]):
    def test_slice(s):
        return (ts.data[s,0] > crop[0]) & (ts.data[s,0] < crop[1])
    
    def crop_slice(s):
        valid_indices = np.nonzero(test_slice(s))[0]
        min_index = np.min(valid_indices)
        max_index = np.max(valid_indices)
        return slice(s.start+min_index,s.start+max_index+1)
    return trajectories(ts.data,[crop_slice(s) for s in ts.slices
    if np.any(test_slice(s))])
        
def left(ts):
    return trajectories(ts.data,[s for s in ts.slices
    if ts.data[s.start,0] > ts.data[s.stop,0]])
        
def right(ts):
    return trajectories(ts.data,[s for s in ts.slices
    if ts.data[s.start,0] < ts.data[s.stop,0]])
        
def crossindices(ts,center=25.0):
    return np.array([next(i+s.start for i,x in enumerate(ts.data[s,0]) if x < center)
    for s in ts.slices[1:]])
        
def genfromtxt(path):
    trajectoriespath = os.path.join(path, 'Analysis/trajectories.csv')
    data = np.genfromtxt(trajectoriespath)
    return scale(crop(crossings(trajectories(data))))
    