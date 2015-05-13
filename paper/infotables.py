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
    
def anylesion(info):
    return info[lesionvolume(info) > 0]
    
def names(info):
    return info.reset_index('subject')['subject'].unique()
    
def cagemates(info):
    return info['cagemate'].unique()
    
def _charrange_(stop):
    s = ord('a')
    return [chr(s+i) for i in range(stop)]    
    
def lesionordermap(info):
    volume = lesionvolume(info)
    volume = volume[volume > 0]
    volume.sort(ascending=False,inplace=True)
    volume = volume.to_frame().join(info)
    lid = names(volume)
    cid = cagemates(volume)
    lname = ['L'+n for n in _charrange_(len(lid))]
    cname = ['C'+n for n in _charrange_(len(cid))]
    return dict(zip(cid,cname)+zip(lid,lname))
