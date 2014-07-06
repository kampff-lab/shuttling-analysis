# -*- coding: utf-8 -*-
"""
Created on Tue Oct 08 15:30:51 2013

@author: IntelligentSystems
"""

import os
import pandas
import itertools
import load_data
import numpy as np
import video_player
import subprocess
import process_trajectories
import plot_utilities as pltutils
import matplotlib.pyplot as plt

if not 'data' in locals():
#    data = load_data.load_pickle(r'G:/Homework/trajectories.pickle')
    data = load_data.load_pickle(r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/trajectories_week1.pickle')
    process_trajectories.rebase_video_path(data,'D:')

width_pixel_to_cm = 50.0 / 1280.0
frames_per_second = 120.0

crop=[100,1100]
traj = data[0][4].trajectories
slices = process_trajectories.clump_trajectories(traj,crop)
trajectory_interval = [len(traj[x,0]) / frames_per_second for x in slices[1:]]
progression_speed = [np.diff(traj[x,0]) * width_pixel_to_cm * frames_per_second for x in slices[1:]]
average_speed = [np.mean(s) for s in progression_speed]

def clump_trajectories(trajectories,crop=[0,1300],minpathlength=100):
    mask = np.ma.masked_outside(trajectories[:,0],crop[0],crop[1])
    clump_slices = np.ma.clump_unmasked(mask)
    return [(s,'right' if trajectories[s.start,0] < 640 else 'left') for s in clump_slices
    if s.stop - s.start >= minpathlength
    and trajectories[s.start,1] < 650]

def get_performance_curves(animal,data):
    trajs = [s.trajectories for s in data[animal]]
    slices = [process_trajectories.clump_trajectories(traj,crop) for traj in trajs]
    intervals = [[len(traj[x,:]) / frames_per_second for x in s[1:]] for traj,s in zip(trajs,slices)]
    return [np.mean(i) for i in intervals],[np.std(i) for i in intervals]
    
def get_shuttling_learning_curve(animal,data,session=0):
    traj = data[animal][session].trajectories
    slices = clump_trajectories(traj,crop)
    intervals = [(x.stop-x.start) / frames_per_second for x in slices]
    return intervals
    
    
    
def plot_performance_curves(p,c):
    plt.errorbar(range(len(p[0])),p[0],p[1],color=c)
    
[plot_performance_curves(get_performance_curves(i,data),'r' if i % 2 == 0 else 'b') for i in range(14)]
plt.xlim(xmin=-0.5)
plt.ylabel('duration (s)')
plt.xlabel('sessions')

[plot(get_shuttling_learning_curve(i,data),color='r' if i % 2 == 0 else 'b') for i in range(14)]

def get_trajectory_slices(animal,session,data):
    traj = data[animal][session].trajectories
    slices = process_trajectories.clump_trajectories(traj,crop)
    return slices

def get_shuttling_curve(animal,data):
    perf = [get_shuttling_learning_curve(animal,data,i) for i in range(5)]
    p = np.array([x for x in itertools.islice(flatten(itertools.chain(perf)),100)])
    return pandas.rolling_mean(p,10)[9:]

[plot(get_shuttling_curve(i,data),color='r' if i % 2 == 0 else 'b') for i in range(14)]

#################### VIDEO INSPECTION #########################################
def play_video_data(path,datapath,playbackrate=0,startframe=0,endframe=None):
    videoplayerpath = r'D:/Bonsai/Bonsai.DataPlayer/Bonsai.VideoPlayer/bin/x64/Release/Bonsai.VideoPlayer.exe'
    args = [videoplayerpath,path,datapath,str(playbackrate),str(startframe)]
    if endframe is not None:
        args.append(str(endframe))
    subprocess.Popen(args)

def play_video_trajectory_data(data,animal,session):
    video = data[animal][session].video
    datafile = os.path.join(os.path.split(video)[0], 'Analysis/trajectories.csv')
    play_video_data(video,datafile,0)

def play_slice_video(data,animal,session,trial):
    traj = data[animal][session].trajectories
    slices = process_trajectories.clump_trajectories(traj,crop)
    video_player.play_video(data[animal][session].video,0,slices[trial].start,slices[trial].stop)
    
def plot_slice_video(data,animal,session,trial):
    traj = data[animal][session].trajectories
    slices = process_trajectories.clump_trajectories(traj,crop)
    plot(traj[slices[trial]])
    
def get_slice_video(data,animal,session,trial):
    traj = data[animal][session].trajectories
    slices = process_trajectories.clump_trajectories(traj,crop)
    return traj,slices[trial]

#################### MOTOR CURVES #########################################
def get_motor_learning_curve(animal,data,trials):
    traj = data[animal][0].trajectories
    s = process_trajectories.clump_trajectories(traj,crop)
    return [(s[i].stop-s[i].start) / frames_per_second for i in trials]
    
curves = []
curves.append(get_motor_learning_curve(0,data,range(5,9)))
curves.append(get_motor_learning_curve(1,data,[2,5,6]) + [(1505-1206) / frames_per_second])
curves.append(get_motor_learning_curve(2,data,range(1,5)))
curves.append(get_motor_learning_curve(3,data,range(2,6)))
curves.append(get_motor_learning_curve(4,data,range(4,8)))
curves.append(get_motor_learning_curve(5,data,range(5,9)))
curves.append(get_motor_learning_curve(6,data,range(3,7)))
curves.append(get_motor_learning_curve(7,data,range(2,6)))
curves.append(get_motor_learning_curve(8,data,range(0,4)))
curves.append(get_motor_learning_curve(9,data,[6,8,9,10]))
curves.append([(4207-3975) / frames_per_second] + get_motor_learning_curve(10,data,[2,3,4]))
curves.append(get_motor_learning_curve(11,data,range(2,6)))
curves.append(get_motor_learning_curve(12,data,[1,2,3,5]))
curves.append(get_motor_learning_curve(13,data,range(5,9)))
lesioncurves = np.array([c for i,c in enumerate(curves) if i % 2 == 0])
shamcurves = np.array([c for i,c in enumerate(curves) if i % 2 != 0])

[plot([1,2,3,4],c,color='r' if i % 2 == 0 else 'b',alpha=0.3) for i,c in enumerate(curves)]
plot([1,2,3,4],np.mean(lesioncurves,axis=0),'r',linewidth=3)
plot([1,2,3,4],np.mean(shamcurves,axis=0),'b',linewidth=3)
plt.xticks([1,2,3,4])
plt.xlabel('trials')
plt.ylabel('duration (s)')


#def bind_trial_video(video,fig):
#    def onclick(event):
#        if event.button == 3:
#            x = int(round(event.xdata))
#            video_player.play_video(video,0,x)
#    fig.canvas.mpl_connect('button_press_event',onclick)