# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 01:02:41 2013

@author: kampff
"""

import os
import ethogram as etho
import matplotlib.pyplot as plt

def plot_2trial_learning(datafolder):
    left0 = os.path.join(datafolder,'Analysis/StepAnnotations/Trial0/left_steps.csv')
    right0 = os.path.join(datafolder,'Analysis/StepAnnotations/Trial0/right_steps.csv')
    left1 = os.path.join(datafolder,'Analysis/StepAnnotations/Trial1/left_steps.csv')
    right1 = os.path.join(datafolder,'Analysis/StepAnnotations/Trial1/right_steps.csv')
    timestamps = os.path.join(datafolder,'front_video.csv')
    
    l0 = etho.load_events(left0)
    r0 = etho.load_events(right0)
    l1 = etho.load_events(left1)
    r1 = etho.load_events(right1)
    offset = etho.load_events(timestamps,slice(1))
    etho.plot_event_sets([l0,r0],None,offset.timestamp,colors=['r','b'])
    etho.plot_event_sets([l1,r1],None,offset.timestamp,colors=['r','b'])
    plt.ylim(ymin=0)
    plt.xlabel('time (seconds)')
    