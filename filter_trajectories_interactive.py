# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 15:52:05 2013

@author: gonca_000
"""

import os
import load_data
import video_player
import matplotlib.pyplot as plt

def save_filtered_trajectories(filename,session,slices=None):
    filtered = filter_trajectories(session.trajectories,session.slices if slices is None else slices,session.video)
    load_data.save_pickle(filename,filtered)

def filter_session_trajectories(session):
    return filter_trajectories(session.trajectories,session.slices,session.video)

def filter_trajectories(trajectories,slices,video):
    datafile = os.path.join(os.path.split(video)[0], 'Analysis/trajectories.csv')
    fig = plt.figure()
    plt.hold(False)
    plt.ion()
    
    key = ['b']
    def press(event):
        key[0] = event.key
    
    result = []
    fig.canvas.mpl_connect('key_press_event', press)
    for sl in slices:
        s = sl
        plt.plot(trajectories[s, :])
        print 'action? ((i)gnore/(c)oncat/(k)eep/escape/(v)iew/(m)irror)',
        
        ans = None
        while ans is None:
            plt.waitforbuttonpress()
            ans = key[0]
            if ans == 'v':
                video_player.play_video_data(video,datafile,0,s.start)
                ans = None
            if ans == 'm':
                s = slice(s.stop,s.start,-1 if s.step == None else None)
                plt.plot(trajectories[s, :])
                ans = None
        
        print ans
        if ans == 'escape':
            break
        if ans == 'k':
            result.append(s)
        if ans == 'c':
            if len(result) == 0:
                result.append(s)
            else:
                result[-1] = slice(result[-1].start,s.stop)
    plt.close(fig)
    return result