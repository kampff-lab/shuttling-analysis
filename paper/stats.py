# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 18:13:31 2014

@author: IntelligentSystem
"""

import scipy.stats as stats

def meanstd(x,axis=None):
    return stats.nanmean(x,axis),stats.nanstd(x,axis)