# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:26:47 2012

@author: IntelligentSystems
"""

import numpy as np
from matplotlib import *

def time_color_map(data):
    colormap = plt.cm.jet
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(data))])

def plot_trajectories(crossings):
    plt.figure('trial-by-trial trajectories')
    time_color_map(crossings)
    for trial in crossings:
        points = trial[trial[0:,0] > -1]
        points[0:,0] = points[0:,0] - 650
        flip = points[0,0] > 0
        if flip:
            points[0:,0] = -points[0:,0]
        plot(points[0:,0],points[0:,1])
    plt.ylim(plt.ylim()[::-1])

def plot_trajectories_x(crossings):
    plt.figure('trial-by-trial progression/time')
    time_color_map(crossings)
    for trial in crossings:
        points = trial[trial[0:,0] > -1]
        points[0:,0] = points[0:,0] - 650
        flip = points[0,0] > 0
        if flip:
            points = -points
        plot(points[0:,0])
    plt.ylim(plt.ylim()[::-1])
    
def plot_trajectories_y(crossings):
    plt.figure('trial-by-trial height/time')
    time_color_map(crossings)
    for trial in crossings:
        points = trial[trial[0:,0] > -1]
        plot(points[0:,1])
    plt.ylim(plt.ylim()[::-1])
    
def compute_performance(crossings):
    return [len(trial[trial[0:,0] > -1]) for trial in crossings]
    
def plot_performance(crossings):
    plt.figure('performance/trials')
    durations = compute_performance(crossings)
    plot(durations,'.')
    
def plot_all(crossings):
    plt.close('all')
    plot_trajectories(crossings)
    plot_trajectories_x(crossings)
    plot_trajectories_y(crossings)
    plot_performance(crossings)
    
def plot_end_to_end(data):
    offset = 0
    for session in data:
        sessionlen = len(session)
        indices = range(offset,offset+sessionlen)
        offset += sessionlen
        plot(indices,session,'.')