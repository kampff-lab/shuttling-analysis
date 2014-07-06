# -*- coding: utf-8 -*-
"""
Created on Tue Sep 03 00:39:51 2013

@author: gonca_000
"""

import os
import load_data
import numpy as np
import ethogram as etho
import matplotlib.pyplot as plt
import plot_session as pltses
import process_session as procses
from daily_plots import save_figure
import plot_utilities as pltutils
import matplotlib.ticker as ticker
import scipy.stats as stats

def get_2trial_step_events(datafolder):
    left0 = os.path.join(datafolder,'StepAnnotations/Trial0/left_steps.csv')
    right0 = os.path.join(datafolder,'StepAnnotations/Trial0/right_steps.csv')
    left1 = os.path.join(datafolder,'StepAnnotations/Trial1/left_steps.csv')
    right1 = os.path.join(datafolder,'StepAnnotations/Trial1/right_steps.csv')
    timestamps = os.path.join(datafolder,'../front_video.csv')
    l0 = etho.load_events(left0)
    r0 = etho.load_events(right0)
    l1 = etho.load_events(left1)
    r1 = etho.load_events(right1)
    offset = etho.load_events(timestamps,slice(1))
    return l0,r0,l1,r1,offset

storage_base = u'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/'
talk_figures = storage_base + u'/publications/MC Lesion-Sham, Gonçalo Lopes/figures'
folders = [r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38', r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39']

############# Data Set Loading ################################################

if not 'mclesionsham' in locals():
    mclesionsham = [load_data.load_path(path,slice(None),False) for path in folders]
    
color_cycle = ['r' if i % 2 == 0 else 'b' for i in range(len(folders))]
big_geometry = (640,345,960,532)

############# I.b Fast Learning on Single Trials ##################

#group_order = [0,2,4,6,8,10,12,1,3,5,7,9,11,13]

# LESION -> CONTROL
group_order = [0,4,12,2,10,8,6,1,5,13,3,11,9,7]
group_cycle = ['r']*7+['b']*7
group_cycle_jp20out = ['r']*6+['b']*7

# CONTROL -> LESION
group_order = [1,5,13,3,11,9,7,0,4,12,2,10,8,6]
group_cycle = ['b']*7+['r']*7

stepevents = np.array([get_2trial_step_events(animal[0].path[0]) for animal in mclesionsham])

def plot_stepevents(l0,r0,l1,r1,yoffset):
    xoffset = min(l0[0],r0[0],lambda e:e.timestamp).timestamp
    etho.plot_event_sets([l0,r0],None,xoffset,yoffset,0,['r','g'],alpha=0.70)
    etho.plot_event_sets([l1,r1],None,xoffset,yoffset,0,['r','g'],alpha=0.70)

plt.close('all')
fig = plt.figure('step times on the first trials')
[plot_stepevents(l0,r0,l1,r1,i) for i,(l0,r0,l1,r1,offset) in
enumerate(get_2trial_step_events(mclesionsham[i][0].path[0]) for i in group_order)]
save_figure(fig,talk_figures)

############# I.c Average Trial Times Across Stable Sessions ##################
plt.close('all')
fig = plt.figure('stable sessions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[pltses.plot_average_trial_times('stable sessions',mclesionsham[i][0:4],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(14)]
pltutils.fix_font_size()
plt.legend(('lesion','sham'))
plt.title('average trial time across stable sessions')
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.png',dpi=100)
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.c Average Trial Times Across Stable Sessions (SHIFT)###########
scale = 46
offsetscale = 2
plt.close('all')
fig = plt.figure('stable sessions average trial times')
ax = fig.gca()
ax.set_color_cycle(group_cycle)
[pltses.plot_average_trial_times('stable sessions',mclesionsham[group_order[i]][0:5],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*2,scale=46) for i in range(14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset,scale*3+tickoffset])
ax.set_xticklabels([0,1,2,3])
plt.draw()
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.png',dpi=100)
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.d Average Trial Times Across Stable Sessions (POPULATION MEAN) ###############
def plot_epoch_average(data,label=None,offset=0,scale=1):
    mean = [np.mean(epoch) for epoch in data]
    std = [np.std(epoch) for i,epoch in enumerate(data)]
    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.IndexLocator(1,0))
    #c = next(ax._get_lines.color_cycle)
    x = (np.arange(len(data))*scale)+offset
    #plt.plot(x,mean,'--',zorder=0,color=c)
    plt.errorbar(x,mean,std,fmt=None,label=label,zorder=100,capthick=0,alpha=0.4)
    plt.xlim(-0.5-offset/2,(len(data)*scale)-0.5)

def plot_average_trial_times(name,sessions,label=None,offset=0,scale=1,makefig=True):
    trial_times = [[i.total_seconds() for i in session.inter_reward_intervals]
                   if len(session.inter_reward_intervals) > 0
                   else [procses.get_session_duration(session).total_seconds()]
                   for session in sessions]
    plot_epoch_average(trial_times,label,offset,scale)
    
def get_average_trial_time(session):
    return np.mean([d.total_seconds() for d in mclesionsham[i][s].inter_reward_intervals])

scale = 46
offsetscale = 2
fig = plt.figure('stable sessions2 average trial times')
ax = fig.gca()
ax.set_color_cycle(group_cycle)
[plot_average_trial_times('stable2 sessions',mclesionsham[group_order[i]][0:5],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*2,scale=46) for i in range(14)]

lesionoffset = 3*offsetscale
lesioncenter = [scale*i+lesionoffset for i in range(5)]
lesion_times = [[get_average_trial_time(mclesionsham[i][s]) for i in group_order[0:7]] for s in range(5)]
plt.errorbar(lesioncenter,[np.mean(x) for x in lesion_times],[np.std(x) for x in lesion_times],fmt='o',color='r',ecolor='k',linewidth=2,capthick=2,markersize=0)

controloffset = 10*offsetscale
controlcenter = [scale*i+controloffset for i in range(5)]
control_times = [[get_average_trial_time(mclesionsham[i][s]) for i in group_order[7:14]] for s in range(5)]
plt.errorbar(controlcenter,[np.mean(x) for x in control_times],[np.std(x) for x in control_times],fmt='o',color='b',ecolor='k',linewidth=2,capthick=2,markersize=0)

pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([scale*i+tickoffset for i in range(5)])
ax.set_xticklabels([0,1,2,3,4])
plt.draw()

############# I.c Average Trial Times Across Stable Sessions (BROKEN AXIS)###########
scale = 46
offsetscale = 2
plt.close('all')
fig,(axh,ax) = plt.subplots(1,2)
ax.set_color_cycle(group_cycle)
axh.set_color_cycle(group_cycle)

plt.sca(axh)
[pltses.plot_average_trial_times('stable sessions',mclesionsham[group_order[i]][slice(0,1)],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*2,scale=46,makefig=False) for i in range(14)]
axh.set_xticks([tickoffset])
axh.set_xticklabels([0])
pltutils.fix_font_size()

plt.sca(ax)
[pltses.plot_average_trial_times('stable sessions',mclesionsham[group_order[i]][1:5],label='lesion' if group_cycle[i] == 'r' else 'control',offset=i*2,scale=46,makefig=False) for i in range(14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset,scale*3+tickoffset])
ax.set_xticklabels([1,2,3,4])

axh.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
axh.yaxis.tick_left()
axh.tick_params(labelright='off') # don't put tick labels on the right
ax.yaxis.tick_right()
plt.draw()
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.png',dpi=100)
#fig.savefig(r'G:/symposium/performance/average_trial_times_stable_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.d Average Trial Times Across Unstable Sessions ##################
plt.close('all')
fig = plt.figure('center unstable sessions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[pltses.plot_average_trial_times('center unstable sessions',mclesionsham[i][6:11],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(14)]
pltutils.fix_font_size()
plt.ylim(-60,1000)
plt.legend(('lesion','sham'))
plt.title('average trial time across center unstable sessions')
fig.savefig(r'G:/symposium/performance/average_trial_times_unstable_sessions.png',dpi=100)
fig.savefig(r'G:/symposium/performance/average_trial_times_unstable_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.d Average Trial Times Across Randomized Sessions ##################
plt.close('all')
fig = plt.figure('randomized sessions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[pltses.plot_average_trial_times('randomized sessions',mclesionsham[i][13:17],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(14)]
pltutils.fix_font_size()
plt.ylim(-60,200)
plt.legend(('lesion','sham'))
plt.title('average trial time across center random sessions')
fig.savefig(r'G:/symposium/performance/average_trial_times_random_sessions.png',dpi=100)
fig.savefig(r'G:/symposium/performance/average_trial_times_random_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.d Average Trial Times Across Fully Released Sessions ##################
plt.close('all')
fig = plt.figure('released sessions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[pltses.plot_average_trial_times('released sessions',mclesionsham[i][-2:],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(14)]
pltutils.fix_font_size()
plt.ylim(-60,400)
plt.legend(('lesion','sham'))
plt.title('average trial time across fully released sessions')
fig.savefig(r'G:/symposium/performance/average_trial_times_released_sessions.png',dpi=100)
fig.savefig(r'G:/symposium/performance/average_trial_times_released_sessions.pdf')
#save_figure(fig,talk_figures)

############# I.d Average Trial Times Across Conditions ##################
plt.close('all')
fig = plt.figure('conditions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
[pltses.plot_average_trial_times('conditions',[mclesionsham[i][s] for s in [4,10,len(mclesionsham[i])-1]],label='lesion' if color_cycle[i] == 'r' else 'sham') for i in range(14)]
pltutils.fix_font_size()
plt.legend(('lesion','sham'))
plt.title('average trial time across assay conditions')
ax.set_xticklabels(['stable','center unstable','all released'])
plt.xlabel('')
plt.ylim(-100,500)

############# I.d Average Trial Times Across Conditions (SHIFT) ###############
scale = 46
offsetscale = 2
plt.close('all')
fig = plt.figure('conditions average trial times')
ax = fig.gca()
ax.set_color_cycle(group_cycle)
[plot_average_trial_times('conditions',[mclesionsham[group_order[i]][s] for s in ([4,10,len(mclesionsham[group_order[i]])-1] if i > 0 else [4])],label='lesion' if group_cycle[i] == 'r' else 'sham',offset=i*2,scale=46) for i in range(0,14)]
pltutils.fix_font_size()
handles, labels = ax.get_legend_handles_labels()
plt.legend((handles[0],handles[7]),(labels[0],labels[7]))
tickoffset = 6.5*offsetscale
ax.set_xticks([tickoffset,scale+tickoffset,scale*2+tickoffset])
ax.set_xticklabels(['stable','center unstable','all released'])
plt.xlabel('')
plt.xlim(xmax=140)
plt.draw()

############# I.d Average Trial Times Across Groups Across Conditions ##################
plt.close('all')
fig = plt.figure('conditions average trial times')
ax = fig.gca()
ax.set_color_cycle(color_cycle)
trial_times = [[procses.get_trial_times(mclesionsham[i][s]) for s in [4,10,len(mclesionsham[i])-1]] for i in range(14)]
trial_time_stats = [[(np.mean(s),np.std(s)) for s in animal] for animal in trial_times]

trial_time_stable = [animal[0] for animal in trial_times]
plt.boxplot([trial_time_stable[i] for i in group_order])

pltutils.fix_font_size()
plt.legend(('lesion','sham'),loc='lower right')
plt.title('average trial time across assay conditions')
ax.set_xticklabels(['stable','center unstable','all released'])
plt.xlabel('')