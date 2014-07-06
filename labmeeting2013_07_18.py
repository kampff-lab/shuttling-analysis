# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 19:53:49 2013

@author: IntelligentSystems
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
import parse_session
from scipy.stats.stats import nanmean, nanstd, sem

def rebase_video_path(experiment,newdeviceroot):
    for i in range(len(experiment)):
        for j in range(len(experiment[i])):
            rootedpath = os.path.splitdrive(experiment[i][j])[1]
            experiment[i][j] = os.path.join(newdeviceroot, rootedpath)

if not 't' in locals():
    t = load_pickle(r'D:/Homework/trajectories.pickle')
    rebase_video_path(t.videos,'D:')
    
def hline(y):
    xlims = plt.gca().get_xlim()
    plt.hlines(y,xlims[0],xlims[1])
    
def vline(x):
    ylims = plt.gca().get_ylim()
    plt.vlines(x,ylims[0],ylims[1])

# Generate clips for all specified session trajectories
def load_session_clips(t,i,j,labelfilter=None):
    currdir = os.getcwd()
    subfolder = proctraj.get_analysis_path(t.videos[i][j])
    session = parse_session.parse_session(subfolder,'jp' + str(i),False)
    shuttling_analysis.make_clips(session.frame_time,t.slices[i][j],t.labels[i][j],t.videos[i][j],labelfilter=labelfilter)
    shuttling_analysis.update_clipdirectories(session.path,currdir)
    return session
    
def load_session_path_clips(path,name,labelfilter=None):
    currdir = os.getcwd()
    subfolder = proctraj.get_analysis_path(path)
    session = parse_session.parse_session(subfolder,name,True)
    shuttling_analysis.make_crossing_clips([session],labelfilter=labelfilter)
    shuttling_analysis.update_clipdirectories(session.path,currdir)
    return session
    
### MANIPULATION ETHOGRAM ###
    
manipulation_sessions = [
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_12-14_59/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_19-12_45/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_26-14_25/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_03-15_32/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_12-10_43/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_12-12_33/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_05-12_21/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_12-14_26/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_19-13_20/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_03-16_06/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_12-11_16/Analysis',
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_12-12_00/Analysis']
    
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
    
ethograms = [load_ethogram(path + r'/ethogram.csv') for path in manipulation_sessions]

fig = plt.figure()
ax = fig.add_subplot(111)
[plot_ethogram(etho,'jpak',(len(ethograms)-1)*2-i*2) for i,etho in enumerate(ethograms)]
ytks = [i*2+0.5 for i in range(len(ethograms))]
rats = [39,37,29,27,25,23,21,38,36,28,26,24,22,20]
ytklabels = ['jpak' + str(r) for r in rats]
plt.yticks(ytks,ytklabels)
hline(13.5)
xlabel('Time from first contact (seconds)')
xlim([0,3])



lesionfreezetimes = [get_total_freezetime(etho) for etho in ethograms[0:7]]
lesioncrossingtimes = [get_crossing_time(etho) for etho in ethograms[0:7]]
lesioncrossingtimes = [x for x in lesioncrossingtimes if x >= 0]
lesionmeans = [np.mean(lesionfreezetimes),nanmean(lesioncrossingtimes)]
lesionerr= [[0,0],[sem(lesionfreezetimes),sem(lesioncrossingtimes)]]

shamfreezetimes = [get_total_freezetime(etho) for i,etho in enumerate(ethograms[7:])]
shamcrossingtimes = [get_crossing_time(etho) for etho in ethograms[7:]]
shamcrossingtimes = [x for x in shamcrossingtimes if x >= 0]
shammeans = [np.mean(shamfreezetimes),nanmean(shamcrossingtimes)]
shamerr = [[0,0],[sem(shamfreezetimes),sem(shamcrossingtimes)]]

fig = plt.figure()
ax = fig.add_subplot(111)
barwidth = 0.35
ind = np.arange(2)
rects1 = plt.bar(ind,lesionmeans,barwidth,color='r',yerr=lesionerr,ecolor='k')
rects2 = plt.bar(ind+barwidth,shammeans,barwidth,color='g',yerr=shamerr,ecolor='k')
plt.xticks(ind+barwidth,('Freeze time', 'Crossing time'))
plt.ylabel('Time (frames)')
plt.legend((rects1[0],rects2[0]),('Lesion','Sham'),loc='Lower Right')
plt.show()

lesionmeancrossingtime = np.mean(lesioncrossingtimes)


s = load_session_clips(t,0,5,{'state':'unstable'}) # jp20 - manip1

s = load_session_clips(t,13,11,{'state':'stable'}) # jp20 - backtostable1

s = load_session_path_clips(
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_12-10_43/Analysis',
'jp36',
{'state':'unstable'}) # jp20 - manip1

s = load_session_path_clips(
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_12-11_16/Analysis',
'jp37',
{'state':'unstable'}) # jp20 - manip1

s = load_session_path_clips(
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_12-12_33/Analysis',
'jp38',
{'state':'unstable'}) # jp20 - manip1

s = load_session_path_clips(
r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_12-12_00/Analysis',
'jp39',
{'state':'unstable'}) # jp20 - manip1


#############################    
    
### STEP ALIGNED TRAJECTORIES ON RANDOM TRIALS ###    
def get_filter_indices(labelfilter,labels):
    return [i for i,label in enumerate(labels) if utils.is_dict_subset(labelfilter,label)]
    
def filter_data(data,labelfilter,labels):
    return [data for data,label in zip(data,labels) if utils.is_dict_subset(labelfilter,label)]
    
def get_roi_step_aligned_data(data,labels,steps,slices,before=120,after=120):
    steps = np.array(steps)
    slices = np.array(slices)
    slsidx = get_filter_indices({'direction':'left','state':'stable'},labels)
    ulsidx = get_filter_indices({'direction':'left','state':'unstable'},labels)
    isls = procsteps.get_first_step_onsets(steps[slsidx],4)
    iuls = procsteps.get_first_step_onsets(steps[ulsidx],4)
    isls = [stepidx + sl.start for stepidx,sl in zip(isls,slices[slsidx]) if stepidx is not None]
    iuls = [stepidx + sl.start for stepidx,sl in zip(iuls,slices[ulsidx]) if stepidx is not None]
    slt = proctraj.get_aligned_data(data,isls,before,after)
    ult = proctraj.get_aligned_data(data,iuls,before,after)
    return slt,ult
    
def get_step_aligned_data(s,data,before=120,after=120):
    sls = np.genfromtxt(os.path.join(s.path[0],'stable_left_steps.csv'),dtype=str,usecols=1)
    uls = np.genfromtxt(os.path.join(s.path[0],'unstable_left_steps.csv'),dtype=str,usecols=1)
    isls = [index(s.frame_time,tm) for tm in sls]
    iuls = [index(s.frame_time,tm) for tm in uls]
    slt = proctraj.get_aligned_data(data,isls,before,after)
    ult = proctraj.get_aligned_data(data,iuls,before,after)
    return slt,ult


def plot_step_aligned_comparison(d1,d2):
    if len(d1) > 0:
        [plt.plot(x,'g',alpha=0.2) for x in d1]
        mslt = mean(d1,axis=0)
        mslterr = std(d1,axis=0)
        plt.plot(mslt,'g',linewidth=2)    
        plt.fill_between(range(len(mslt)),mslt-mslterr,mslt+mslterr,alpha=0.2,color='g')
    if len(d2) > 0:
        [plt.plot(x,'r',alpha=0.2) for x in d2]
        mult = mean(d2,axis=0)
        multerr = std(d2,axis=0)
        plt.plot(mult,'r',linewidth=2)
        plt.fill_between(range(len(mult)),mult-multerr,mult+multerr,alpha=0.2,color='r')
    
def plot_comparison(slt,ult):
    # Progression comparison
    fig = figure()
    slp = [x[:,0] for x in slt]
    ulp = [x[:,0] for x in ult]
    plot_step_aligned_comparison(slp,ulp)
    vline(120)
    plt.gca().invert_yaxis()
    return fig
    
    # Height comparison
#    figure()
#    slh = [x[:,1] for x in slt]
#    ulh = [x[:,1] for x in ult]
#    plot_step_aligned_comparison(slh,ulh)
#    vline(120)
#    plt.gca().invert_yaxis()
    
    # Speed comparison
#    figure()
#    slsp = [diff(x[:,0]) for x in slt]
#    ulsp = [diff(x[:,0]) for x in ult]
#    plot_step_aligned_comparison(slsp,ulsp)
#    vline(120)
#    plt.gca().invert_yaxis()    
    
s = load_session_clips(t,0,16) # jp20 - manip1
#
s = load_session_clips(t,0,16,{'direction':'left','state':'unstable'}) # jp21 - manip1
#slt,ult = get_step_aligned_data(s,t.trajectories[1][16])
#

s = load_session_clips(t,5,16,{'direction':'left','state':'stable'}) # jp25 - manip1
slt,ult = get_step_aligned_data(s,t.trajectories[5][16])

s = load_session_clips(t,4,16,{'direction':'left','state':'stable'}) # jp24 - manip1
slt,ult = get_step_aligned_data(s,t.trajectories[4][16])

#### ROI data #####

sub = 9
sess = 14
plts = [get_roi_step_aligned_data(
t.trajectories[sub][sess],
t.labels[sub][sess],
t.steps[sub][sess],
t.slices[sub][sess]) for sub in [0,2,4,6,8,1,3,5,7,9]]


plt.close('all')

figs = [plot_comparison(slt,ult) for slt,ult in plts]

tilefigures(figs,[5,2])
##################################################

######## SLIP DISTRIBUTIONS ######################

slips = [np.genfromtxt(f,usecols=3) for f in [
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_04-11_40/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_04-12_14/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_11-15_20/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_11-14_46/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_18-12_12/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_18-12_46/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_25-14_15/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_25-13_39/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_02-14_35/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_02-15_09/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_11-10_44/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_11-11_18/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_11-12_36/Analysis/slip_activity.csv',
r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_11-12_03/Analysis/slip_activity.csv'
]]

peaks = [utils.find_peaks(slip) for slip in slips]