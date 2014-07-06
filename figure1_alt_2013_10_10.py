# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 01:37:32 2013

@author: gonca_000
"""

import os
import pandas
import operator
import itertools
import load_data
import numpy as np
import video_player
import process_trajectories as proctraj
import plot_utilities as pltutils
import matplotlib.pyplot as plt
import process_session as procses
import plot_session as pltses
import analysis_utilities as utils
import scipy.stats as stats
import filter_trajectories_interactive as filttraj
import figure_utilities

max_height_cm = 24.0
height_pixel_to_cm = max_height_cm / 680.0
width_pixel_to_cm = 50.0 / 1280.0
rail_height_pixels = 100
frames_per_second = 120.0

def scale_height(height):
    return max_height_cm - ((height + rail_height_pixels) * height_pixel_to_cm)

folders = [r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39']
mclesionsham = [load_data.load_path_sessions(folder,[4,10,24 if i < 10 else 18]) for i,folder in enumerate(folders)]

mclesionsham = [load_data.load_path_trajectories(folder,[4,10,24 if i < 10 else 18]) for i,folder in enumerate(folders)]
videos = [load_data.get_path_videos(folder,[4,10,24 if i < 10 else 18]) for i,folder in enumerate(folders)]

mclesionsham = [load_data.load_path_trajectories(folder,[4,10,16,24 if i < 10 else 18]) for i,folder in enumerate(folders)]
videos = [load_data.get_path_videos(folder,[4,10,16,24 if i < 10 else 18]) for i,folder in enumerate(folders)]

[[proctraj.swap_head_tail(s) for s in animal] for animal in mclesionsham[-4:]]

#group_order = [0,2,4,6,8,10,12,1,3,5,7,9,11,13]
valid_positions = [150,1130]

# LESION -> CONTROL
group_order = [0,4,12,2,10,8,6,1,5,13,3,11,9,7]
group_cycle = ['r']*7+['b']*7
group_cycle_jp20out = ['r']*6+['b']*7

# CONTROL -> LESION
group_order = [1,5,13,3,11,9,7,0,4,12,2,10,8,6]
group_cycle = ['b']*7+['r']*7

######################### Preprocess trajectories #############################

slices = [[proctraj.slice_trajectories(s) for s in animal] for animal in mclesionsham]
crossing_slices = [[proctraj.get_center_crossings(mclesionsham[i][j],s) for j,s in enumerate(animal)] for i,animal in enumerate(slices)]
cropped_slices = [[proctraj.crop_slices(mclesionsham[i][j],s,valid_positions) for j,s in enumerate(animal)] for i,animal in enumerate(crossing_slices)]
crossings = [[proctraj.get_sliced_data(mclesionsham[i][j],s) for j,s in enumerate(animal)] for i,animal in enumerate(cropped_slices)]

filtered = [[filttraj.filter_trajectories(t,s,v) for t,v,s in zip(animal,animalv,animalsl)] for animal,animalv,animalsl in zip(mclesionsham,videos,cropped_slices)]

crossings = [[proctraj.get_sliced_data(mclesionsham[i][j],s) for j,s in enumerate(animal)] for i,animal in enumerate(cropped_slices)]

#short_slices = [[proctraj.filter_long_trials(s,1200) for j,s in enumerate(animal)] for i,animal in enumerate(crossing_slices)]

slice_offset = 2
direction_trials = [[[('l' if t[0,0] > 640 else 'r') for t in s[slice_offset:]] for s in animal] for animal in crossings]
height_trials = [[[scale_height(np.mean(t[:,1])) for t in s[slice_offset:]] for s in animal] for animal in crossings]
speed_trials = [[[np.mean(np.abs(np.diff(t[:,0]))) for t in s[slice_offset:]] for s in animal] for animal in crossings]
time_trials = [[[len(t) / 120.0 for t in s[slice_offset:]] for s in animal] for animal in crossings]

############# I.d Average Nose Speed Across Conditions (SHIFT) ################
scale = 46
offsetscale = 2
plt.close('all')
fig = plt.figure('conditions average tip speed across sessions')
ax = fig.gca()
ax.set_color_cycle(group_cycle)
[plot_average_tip_speed('conditions',[mclesionsham[group_order[i]][s] for s in ([0,1,2] if i > 0 else [0])],crop=valid_positions,label='lesion' if group_cycle[i] == 'r' else 'sham',offset=i*2,scale=46,trial_slices=slice(1,None)) for i in range(0,14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
plt.title('average nose speed across assay conditions')
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','center unstable','all released'])
plt.xlabel('')
plt.draw()

######## I.d Nose Speed Distribution Across Conditions Across Groups ##########
def barplot(data,offset,barwidth,color):
    plt.bar(offset,np.mean(data),width=barwidth,yerr=[[0],[np.std(data)]],color=color,ecolor=color)

conditionselector = lambda x:None
average_speed = [
[procses.get_average_crossing_tip_speed(session,conditionselector(session),valid_positions,slice(1,None))[1]
for session in mclesionsham[i]]
for i in range(0,14)]

lesion_stable = np.array(utils.flatten([average_speed[i][0] for i in range(0,14) if i % 2 == 0]))
sham_stable = np.array(utils.flatten([average_speed[i][0] for i in range(0,14) if i % 2 != 0]))
lesion_centerunstable = np.array(utils.flatten([average_speed[i][1] for i in range(0,14) if i % 2 == 0]))
sham_centerunstable = np.array(utils.flatten([average_speed[i][1] for i in range(0,14) if i % 2 != 0]))
lesion_allreleased = np.array(utils.flatten([average_speed[i][2] for i in range(0,14) if i % 2 == 0]))
sham_allreleased = np.array(utils.flatten([average_speed[i][2] for i in range(0,14) if i % 2 != 0]))

### BARPLOT ###
offset=0
barwidth=0.35
barplot(lesion_stable,offset,barwidth,'r')
barplot(sham_stable,offset+barwidth,barwidth,'b')
offset = offset + barwidth * 2 + 0.1
barplot(lesion_centerunstable,offset,barwidth,'r')
barplot(sham_centerunstable,offset+barwidth,barwidth,'b')
offset = offset + barwidth * 2 + 0.1
barplot(lesion_allreleased,offset,barwidth,'r')
barplot(sham_allreleased,offset+barwidth,barwidth,'b')
ax = plt.gca()
ax.set_xticks([barwidth,barwidth*3+0.1,barwidth*5+0.2])
ax.set_xticklabels(['stable','center unstable','all released'])
plt.ylabel('progression speed (cm/s)')
plt.draw()

### BOXPLOT ###
def setBoxColors(bp,i,color):
    plt.setp(bp['boxes'][i], color=color)
    plt.setp(bp['caps'][i*2], color=color)
    plt.setp(bp['caps'][i*2+1], color=color)
    plt.setp(bp['whiskers'][i*2], color=color)
    plt.setp(bp['whiskers'][i*2+1], color=color)
    plt.setp(bp['fliers'][i*2], color=color)
    plt.setp(bp['fliers'][i*2+1], color=color)
    plt.setp(bp['medians'][i], color=color)

bp = plt.boxplot([lesion_stable,sham_stable,lesion_centerunstable,sham_centerunstable,lesion_allreleased,sham_allreleased],positions=[1,2,4,5,7,8])
ax = plt.gca()
ax.set_xticks([1.5,4.5,7.5])
ax.set_xticklabels(['stable','center unstable','all released'])
setBoxColors(bp,0,'r')
setBoxColors(bp,1,'b')
setBoxColors(bp,2,'r')
setBoxColors(bp,3,'b')
setBoxColors(bp,4,'r')
setBoxColors(bp,5,'b')
plt.ylabel('progression speed (cm/s)')

### BOXPLOT AVERAGES ###
mlesion_stable = np.array([np.mean(average_speed[i][0]) for i in range(0,14) if i % 2 == 0])
msham_stable = np.array([np.mean(average_speed[i][0]) for i in range(0,14) if i % 2 != 0])
mlesion_centerunstable = np.array([np.mean(average_speed[i][1]) for i in range(0,14) if i % 2 == 0])
msham_centerunstable = np.array([np.mean(average_speed[i][1]) for i in range(0,14) if i % 2 != 0])
mlesion_allreleased = np.array([np.mean(average_speed[i][2]) for i in range(0,14) if i % 2 == 0])
msham_allreleased = np.array([np.mean(average_speed[i][2]) for i in range(0,14) if i % 2 != 0])

positions = [1,2,4,5,7,8]
bp = plt.boxplot([mlesion_stable,msham_stable,mlesion_centerunstable,msham_centerunstable,mlesion_allreleased,msham_allreleased],positions=positions)
plt.plot([1]*7+[4]*7+[7]*7,utils.flatten([mlesion_stable,mlesion_centerunstable,mlesion_allreleased]),'k+')
plt.plot([2]*7+[5]*7+[8]*7,utils.flatten([mlesion_stable,mlesion_centerunstable,mlesion_allreleased]),'k+')
ax = plt.gca()
ax.set_xticks([1.5,4.5,7.5])
ax.set_xticklabels(['stable','center unstable','all released'])
setBoxColors(bp,0,'r')
setBoxColors(bp,1,'b')
setBoxColors(bp,2,'r')
setBoxColors(bp,3,'b')
setBoxColors(bp,4,'r')
setBoxColors(bp,5,'b')
plt.ylabel('progression speed (cm/s)')


############# I.d Average Nose Height Across Conditions (SHIFT) ###############

def concat_empty(arr):
    if len(arr) == 0:
        return np.empty((0,1))
    return np.concatenate(arr)

#### BARPLOT DRAFT FOR TIME ####
lesion_stable = np.concatenate([animal[0] for animal in time_trials[0:14:2]])
sham_stable = np.concatenate([animal[0] for animal in time_trials[1:14:2]])
lesion_centerunstable = np.concatenate([animal[1] for animal in time_trials[2:14:2]])
sham_centerunstable = np.concatenate([animal[1] for animal in time_trials[1:14:2]])
lesion_allreleased = np.concatenate([animal[2] for animal in time_trials[2:14:2]])
sham_allreleased = np.concatenate([animal[2] for animal in time_trials[1:14:2]])

stats.levene(lesion_stable,sham_stable,center='mean')
stats.levene(lesion_centerunstable,sham_centerunstable,center='mean')
stats.levene(lesion_allreleased,sham_allreleased,center='mean')

stats.ttest_ind(lesion_stable,sham_stable,False)
stats.ttest_ind(lesion_centerunstable,sham_centerunstable,False)
stats.ttest_ind(lesion_allreleased,sham_allreleased,False)

var = np.std
ax = plt.gca()
plt.bar([0,0.8],[np.mean(lesion_stable),np.mean(sham_stable)],yerr=[[0,0],[var(lesion_stable),var(sham_stable)]],color=['r','b'],ecolor='k')
plt.bar([2,2.8],[np.mean(lesion_centerunstable),np.mean(sham_centerunstable)],yerr=[[0,0],[var(lesion_centerunstable),var(sham_centerunstable)]],color=['r','b'],ecolor='k')
plt.bar([4,4.8],[np.mean(lesion_allreleased),np.mean(sham_allreleased)],yerr=[[0,0],[var(lesion_allreleased),var(sham_allreleased)]],color=['r','b'],ecolor='k')
plt.ylabel('time to cross obstacles (s)')
plt.xlabel('x')
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
ax.set_xticks([0.8,2.8,4.8])
ax.set_xticklabels(['stable','center unstable','all released'])
plt.xlabel('')
plt.draw()
#############################################

###### Average time to cross obstacles #####################################
scale = 46
offsetscale = 2
ax = plt.gca()
ax.set_color_cycle(group_cycle)
[pltses.plot_epoch_average([time_trials[group_order[i]][s] for s in ([0,1,2] if i > 0 else [0])],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*offsetscale,scale=scale) for i in range(0,14)]
plt.ylabel('time to cross obstacles (s)')
plt.xlabel('x')
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','partially unstable','fully unstable'])
plt.ylim(ymin=-8,ymax=27)
plt.xlabel('')
plt.draw()

############## Average nose height #####################################
scale = 46
offsetscale = 2
ax = plt.gca()
ax.set_color_cycle(group_cycle)
[pltses.plot_epoch_average([height_trials[group_order[i]][s] for s in ([0,1,2] if i > 0 else [0])],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*offsetscale,scale=scale) for i in range(0,14)]
plt.ylabel('nose height (cm)')
plt.xlabel('x')
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','partially unstable','fully unstable'])
plt.xlabel('')
plt.draw()

######### Average time to cross obstacles 2 (JP20 out?) ############################
scale = 46
offsetscale = 2
ax = plt.gca()
ax.set_color_cycle(group_cycle_jp20out)
[pltses.plot_epoch_average(time_trials[group_order[i]],label='lesion' if group_cycle[i-1] == 'r' else 'sham',offset=i*offsetscale,scale=scale) for i in range(1,14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
plt.title('average nose height across assay conditions')
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','center unstable','all released'])
ax.invert_yaxis()
plt.xlabel('')
plt.draw()

########### Average nose height ############################
scale = 46
offsetscale = 2
fig = plt.figure('conditions average tip height across sessions')
ax = fig.gca()
ax.set_color_cycle(group_cycle_jp20out)
[pltses.plot_average_tip_height('conditions',[mclesionsham[group_order[i]][s] for s in [0,1,2]],crop=valid_positions,label='lesion' if group_cycle[i-1] == 'r' else 'sham',offset=i*2,scale=46) for i in range(1,14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
plt.title('average nose height across assay conditions')
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','center unstable','all released'])
ax.invert_yaxis()
plt.xlabel('')
plt.draw()

########## Measurements for video picking ###########
def get_fastest_left_trials(i,s):
    a = group_order[i]
    fastest_index = np.argmin([np.inf if d == 'r' else t for t,d in zip(time_trials[a][s],direction_trials[a][s])])
    return cropped_slices[a][s][fastest_index+slice_offset]

fastest_stable = [get_fastest_left_trials(i,0) for i in range(len(time_trials))]
fastest_partial = [get_fastest_left_trials(i,1) for i in (range(0,7)+range(8,14))]
fastest_unstable = [get_fastest_left_trials(i,2) for i in (range(0,7)+range(8,14))]


########## Measurements for paper ###################

plt.figure(figsize=(4,7))
plot_trial_measures(group_cycle,group_order,time_trials,xticklabels=['stable','partial','random','unstable'])
plt.ylabel('time to cross obstacles (s)')
plt.xlabel('')
plt.draw()

plt.figure(figsize=(4,7))
plot_trial_measures(group_cycle,group_order,height_trials,0.1,0.2,ylims=[-1,7.5],xticklabels=['stable','partial','random','unstable'])
plt.ylabel('nose height (cm)')
plt.xlabel('')
plt.draw()