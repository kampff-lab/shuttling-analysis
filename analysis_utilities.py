# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import csv
import errno
import string
import numpy as np
import scipy.stats as stats
import bisect

### Defining enums ###

def roundup(a,decimals=0):
    exponent = np.power(10,decimals)
    num = a * exponent
    if np.modf(num)[0] * 10 > 0:
        num = num + 1
    return np.modf(num)[1] / exponent

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

### Searching sorted lists ###

def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError

def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect.bisect_left(a, x)
    if i:
        return a[i-1]
    raise ValueError

def find_le(a, x):
    'Find rightmost value less than or equal to x'
    i = bisect.bisect_right(a, x)
    if i:
        return a[i-1]
    raise ValueError

def find_gt(a, x):
    'Find leftmost value greater than x'
    i = bisect.bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

##############################

def gmax(iterator):
    return [x for x in igmax(iterator)]

def igmax(iterator):
    for x in iterator:
        yield max(x)

def split_list_pairwise(l,p):
    groups = []
    prev = None
    group = None
    for x in l:
        if prev is None or p(x,prev):
            group = []
            groups.append(group)
        group.append(x)
        prev = x
    return groups

def rebase_path(path,newletter):
    return os.path.join(newletter,os.path.splitdrive(path)[1])

def is_dict_subset(sd,d):
    for item in sd.items():
        val = d.get(item[0])
        if val != item[1]:
            return False
    return True

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def removenan(x):
    x = np.array(x)
    return x[~np.isnan(x)]
    
def removenanrows(x):
    return x[~np.isnan(x).any(axis=1)]
    
def removerows(x,condition):
    return x[~condition.any(axis=1)]

def masknan(x):
    return np.ma.masked_array(x,np.isnan(x))

def nanmean(x):
    x = masknan(x)
    return np.mean(x)

def find_gt(l,v):
    return next((i for i,x in enumerate(l) if x > v), len(l))
        
def find_lt(l,v):
    return next((i for i,x in enumerate(l) if x < v), len(l))
    
def find_between(l,minv,maxv):
    return next((i for i,x in enumerate(l) if x < maxv and x > minv), len(l))

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
            
def align_data(data,indices,before=0,after=0):
    return [data[:,slice(index-before,index+after+1)] for index in indices if index >= 0]

def meanstd(x,axis=None):
    return stats.nanmean(x,axis),stats.nanstd(x,axis)
    
def find_triggers(data,minstep=0,threshold=None):
    triggers = np.diff(np.int32(data > threshold)).nonzero()[0] + 1
    if minstep > 0:
        gpeaks = split_list_pairwise(triggers,lambda x,p:x-p > minstep)
        triggers = np.array([g[np.argmax([data[i] for i in g])] for g in gpeaks])
    return triggers
    
def find_peaks(data,minstep=0,threshold=None):
    peaks = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1 # local max
    if threshold is not None:
        peaks = peaks[data[peaks] > threshold]    
    
    if minstep > 0:
        gpeaks = split_list_pairwise(peaks,lambda x,p:x-p > minstep)
        peaks = np.array([g[np.argmax([data[i] for i in g])] for g in gpeaks])
    return peaks
    
def find_troughs(data):
    return (np.diff(np.sign(np.diff(data))) > 0).nonzero()[0] + 1 # local min
    
def get_peak_statistics(data):
    peaks = find_peaks(data)
    return meanstd(data[peaks])

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