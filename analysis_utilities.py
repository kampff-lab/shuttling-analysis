# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import csv
import string
import numpy as np
import scipy.stats as stats

def find_gt(l,v):
    try:
        return next(i for i,x in enumerate(l) if x > v)
    except StopIteration:
        return len(l)
        
def find_lt(l,v):
    try:
        return next(i for i,x in enumerate(l) if x < v)
    except StopIteration:
        return len(l)

def test_consecutive(x, y):
    if len(x) > 0 and x[-1][-1] == (y-1):
        x[-1].append( y )
    else:
        x.append( [y] )
    return x

def consecutive_elements(l):
    return reduce(test_consecutive,l,[])

def padded_slice(x,start,stop,fillvalue):
    pad_left = 0
    pad_right = 0
    if start < 0:
        pad_left = -start;
    if stop > len(x):
        pad_right = stop - len(x)
    return [fillvalue] * pad_left + x[max(0,start):stop] + [fillvalue] * pad_right

def get_aligned_data(data,indices,before=0,after=0,padinvalid=True):
    if before == 0 and after == 0:
        if padinvalid:
            return [index >= 0 and data[trial][index] or np.nan for trial,index in enumerate(indices)]
        else:
            return [data[trial][index] for trial,index in enumerate(indices) if index >= 0]
    else:
        width = before + after + 1
        if padinvalid:
            return [index >= 0 and padded_slice(data[trial],index-before,index+after+1,np.nan) or [np.nan] * width for trial,index in enumerate(indices)]
        else:
            return [padded_slice(data[trial],index-before,index+after+1,np.nan) for trial,index in enumerate(indices) if index >= 0]

def meanstd(x,axis=None):
    return stats.nanmean(x,axis),stats.nanstd(x,axis)

def ensure_list(x):
    if len(x.shape) < 1:
        return np.array([x])
    return x

def directory_tree(path,level):
    if level > 0:
        return [directory_tree(path + '\\' + name, level-1) for name in os.listdir(path)]
    return path

def loadfromcsv(filename,convert=lambda x:float(x)):
    with open(filename) as file:
        return [[convert(x) for x in string.split(line[0])] for line in csv.reader(file)]
        
def flatten(l):
    return [item for sublist in l for item in sublist]
  
def flatten_slice(l,s):
    return flatten([item[s] for item in l])