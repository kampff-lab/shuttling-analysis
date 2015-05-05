# -*- coding: utf-8 -*-
"""
Created on Mon May 04 18:57:40 2015

@author: Gonçalo
"""

def lesionvolume(info):
    return info['lesionleft'] + info['lesionright']
    
def control(info):
    return info[lesionvolume(info) == 0]
    
def smalllesion(info):
    volume = lesionvolume(info)
    return info[(volume > 0) & (volume <= 15)]
    
def lesion(info):
    return info[lesionvolume(info) > 15]
    
def names(info):
    return info.reset_index('subject')['subject'].unique()
    
def cagemates(info):
    return info['cagemate'].unique()
