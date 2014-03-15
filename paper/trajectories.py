# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 16:12:45 2013

@author: gonca_000
"""

import numpy as np

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