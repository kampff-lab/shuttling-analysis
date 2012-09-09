# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import csv
import string
import numpy as np

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