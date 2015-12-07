# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:51:31 2013

@author: gonca_000
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatch
from load_data import *
from analysis_utilities import *
from process_ethograms import *
import shuttling_analysis
import process_trajectories as proctraj
import process_stepactivity as procsteps
import plot_utilities as pltutils
import parse_session
import dateutil
from scipy.stats.stats import nanmean, nanstd, sem
import video_player
    
def hline(y):
    xlims = plt.gca().get_xlim()
    plt.hlines(y,xlims[0],xlims[1])
    
def vline(x):
    ylims = plt.gca().get_ylim()
    plt.vlines(x,ylims[0],ylims[1])
    
### MANIPULATION ETHOGRAM ###
    
paths = np.array([r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_05-12_21/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_12-14_59/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_12-14_26/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_19-12_45/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_19-13_20/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_26-14_25/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_03-15_32/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_03-16_06/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_12-10_43/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_12-11_16/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_12-12_33/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_12-12_00/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_48/2014_03_07-11_36/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_49/2014_03_07-12_10/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_50/2014_03_07-12_56/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_51/2014_03_07-13_31/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_52/2014_03_14-17_02/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_53/2014_03_14-16_25/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_54/2014_03_14-18_25/Analysis',
r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_55/2014_03_14-17_49/Analysis'])
lesion_shuffle = paths[[1,5,13,11,3,19,9,15,21,17,7,   0,4,12,10,2,18,8,14,20,16,6]]
#lesion_shuffle = paths[[1,5,13,3,11,9,7,0,4,12,2,10,8,6]]
#lesion_shuffle = paths[[0,4,12,2,10,8,6,1,5,13,3,11,9,7]]
#lesion_shuffle = paths[[0,2,4,6,8,10,12,1,3,5,7,9,11,13]]
    
def get_total_freezetime(etho):
    freezetime = 0
    ranges = get_ethogram_ranges(etho)
    for i in range(len(ranges[0])):
        if ranges[0][i] == 'Freeze':
            freezetime += ranges[1][i][1]
    return freezetime
    
def get_crossing_time(etho):
    ranges = get_ethogram_ranges(etho)
    for i in range(len(ranges[0])):
        if ranges[0][i] == 'FinishAcross': # or ranges[0][i] == 'GoBack':
            return ranges[1][i][0]
    return np.nan

ethograms = [load_ethogram(path + r'/ethogram.csv') for path in lesion_shuffle]    
blind_ethograms = [load_ethogram(path + r'/blind_ethogram.csv') for path in lesion_shuffle]
blind_ethograms2 = [load_ethogram(path + r'/blind_ethogram2.csv') for path in lesion_shuffle]

def make_ethogram(ethograms,label=True,title=None,legend=True):
    midpoint = int(len(ethograms) / 2)
    [plot_ethogram(etho,'jpak',(len(ethograms)-1)*2-i*2,legend=False) for i,etho in enumerate(ethograms)]
    ytks = [i*2+0.5 for i in range(len(ethograms))]
    #rats = [39,37,29,27,25,23,21,38,36,28,26,24,22,20]
    #ytklabels = ['jpak' + str(r) if label else '' for r in rats]
    ytklabels = [('C' if i < midpoint else 'L') + chr(ord('a')+(i%midpoint)) if label else '' for i in range(len(ethograms)-1,-1,-1)]
    plt.yticks(ytks,ytklabels)
    #hline(13.5)
    hline(ytks[midpoint]-1)
    xlabel('time from first contact (s)')
    xlim([0,30])
    ethogram_artists = [plt.Rectangle((0,0),1,1,fc=color) for color in event_color_scheme.values()[0:4]]
    plt.legend(ethogram_artists,event_color_scheme.keys(),bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if title is not None:
        plt.title(title)

fig = plt.figure()
ax = fig.add_subplot(121)
make_ethogram(ethograms,title='Goncalo',legend=False)

fig = plt.figure()
ax = fig.add_subplot(111)
make_ethogram(blind_ethograms,label=True)
pltutils.fix_font_size()
#make_ethogram(blind_ethograms,label=True,title='ethogram of first contact with manipulated rail')

fig = plt.figure()
ax = fig.add_subplot(111)
make_ethogram(blind_ethograms2,title='Joao Trial 2')

### CLIP GENERATION ###

def write_contact_clips(path,filename='player.csv'):
    timefile = get_timefile(path)
    frame_time = np.genfromtxt(timefile,dtype=str)
    timepoint = np.genfromtxt(path + r'/contact.csv',usecols=1,dtype=str)
    contact_index = utils.index(frame_time,timepoint)
    contact_slice = (frame_time[contact_index-240],frame_time[contact_index+1200])
    shuttling_analysis.write_time_slices(os.path.join(path,filename),[contact_slice])
    return path

currdir = os.getcwd()
clip_shuffle = paths[[1,3,5,7,9,11,13,0,2,4,6,8,10,12]]
contact_clip_directories = [write_contact_clips(path) for path in clip_shuffle]
shuttling_analysis.update_clipdirectories(contact_clip_directories,currdir)


### TIME TO REWARD AFTER MANIPULATION ###

def get_1st_manip_reward_time(path):
    left_reward = np.genfromtxt(path + r'/../left_rewards.csv',dtype=str)[slice(10,11)]
    if len(left_reward) == 0:
        left_reward = [np.genfromtxt(path + '/../front_video.csv',dtype=str)[-1]]
    return left_reward[0]

reward_post_manipulation = np.array([dateutil.parser.parse(get_1st_manip_reward_time(path)) for path in paths])
contact_times = np.array([dateutil.parser.parse(etho[0][1]) for etho in ethograms])
time_to_1st_reward = reward_post_manipulation - contact_times
delay_first_reward = [delta.total_seconds() for delta in time_to_1st_reward]

### MOVEMENT PARAMETERS AROUND MANIPULATION ###

def get_crossings(trajectories,slices,left=200,right=950):
    return [s for s in slices
    if any(trajectories[s][:,0] < left) and any(trajectories[s][:,0] > right)]
        
def swap_head_tail(trajectories):
    trajectories[:,[0,1,2,3]] = trajectories[:,[2,3,0,1]]

trajectories = [np.genfromtxt(path + r'/trajectories.csv') for path in paths]
labels = [proctraj.load_trajectory_labels(path + r'/trajectory_labels.csv') for path in paths]
slices = [proctraj.clump_trajectories(t) for t in trajectories]
[swap_head_tail(trajectory) for trajectory in trajectories[10:14]]

unstable_generator = [(i for i,label in enumerate(session) if label['state'] == 'unstable') for session in labels]
unstable = [next(gen) for gen in unstable_generator]

up1t = np.array([t[s[i-3]] for i,s,t in zip(unstable,slices,trajectories)])
up2t = np.array([t[s[i-2]] for i,s,t in zip(unstable,slices,trajectories)])
u1t = np.array([t[s[i-1]] for i,s,t in zip(unstable,slices,trajectories)])
u2t = np.array([t[s[i+1]] for i,s,t in zip(unstable,slices,trajectories)])

lg = [0,2,4,8,10,12]
cg = [1,3,5,7,11,13]

### PROGRESSION ON MANIPULATION TRIAL ###
def plot_trial_parameter(a,ts,p=0,scale=12/300,label=None,**kwargs):
    t = ts[a][:,p]
    if p==0:
        if t[0] > 640:
            t = 1280-t
    if p==1:
        t = 680-t
    plot(np.arange(len(t))/120,t*scale,label=label,**kwargs)

def plot_trial_comparison(a,p=0,scale=12/300,label=True):
    plot_trial_parameter(a,u1t,p,scale,'before',color='b')
    plot_trial_parameter(a,u2t,p,scale,'after',color='r')
    if label:
        xlabel('Time (seconds)')
    xlim(0,3)
    
def plot_progression(a,label=True):
    scale=12/300
    plot_trial_comparison(a,0,label=label)
    if label:
        ylabel('Progression (cm)')
    
def plot_height(a,label=True):
    plot_trial_comparison(a,1,label=label)
    if label:
        ylabel('Height (cm)')
        
### MANIPULATION PROGRESSION COMPARISON ###
plt.subplot(1,2,1)
[plot_trial_parameter(a,u1t,color='b') for a in lg]
title('Lesion')
xlabel('Time (seconds)')
ylabel('Progression (cm)')
xlim(0,3)
plt.subplot(1,2,2)
[plot_trial_parameter(a,u1t,color='b') for a in cg]
title('Sham/Control')
xlabel('Time (seconds)')
xlim(0,3)

### PROGRESSION BEFORE AND AFTER COMPARISON ###
fig,axs = plt.subplots(6,2,True,True)
axs = axs.ravel()
subjects = [0,1,2,3,4,5,8,7,10,11,12,13]
for i in range(len(subjects)):
    plt.sca(axs[i])
    plot_progression(subjects[i],label=False)
    if i == 0:
        title('Lesion')
        legend(bbox_to_anchor=(0, 0, 0.5, 1), bbox_transform=gcf().transFigure)
    if i == 1:
        title('Sham/Control')
    if i == 4:
        ylabel('Progression (cm)')
    if i > 9:
        xlabel('Time (seconds)')

[plot(trial[:,0],'r') for trial in u1t[lg]]
[plot(trial[:,0],'b') for trial in u1t[cg]]

### RAND ###
base_crossings = [(t,get_crossings(t,s)[3:18]) for t,s in zip(trajectories,slices)]
average_heights = [mean([mean(t[c][:,1]) for c in crossings]) for t,crossings in base_crossings]

### PlAY VIDEOS ###

def play_trial(a,i,s):
    global paths
    video_player.play_video(paths[a] + '/../front_video.avi',10,startframe=s[a][i].start)