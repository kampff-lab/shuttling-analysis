# -*- coding: utf-8 -*-
"""
Created on Fri Jun 07 01:08:54 2013

@author: gonca_000
"""
import os
import ast
import sys
import glob
import pickle
import numpy as np
import itertools as it
import scipy.signal as sig
import numpy.linalg.linalg as ln
import analysis_utilities as utils
import signal_processing as sigproc
import process_stepactivity as procsteps
import shuttling_analysis
import load_data

_dabefore = 150
_daafter = 150
_samplerate = 120.0
_lowpasscutoff = 10.0

def get_aligned_data(x,indices,before,after):
    return [x[slice(idx-before,idx+after+1)] for idx in indices]

def get_analysis_path(videopath):
    return os.path.join(os.path.split(videopath)[0],'Analysis')

def rebase_video_path(experiment,newdeviceroot):
    for a in experiment:
        for s in a:
            path = s.video
            rootedpath = os.path.splitdrive(path)[1]
            s.video = os.path.join(newdeviceroot, rootedpath)
            
def get_crossings(session,left=200,right=950):
    return [s for s in session.slices
    if any(session.trajectories[s][:,0] < left) and any(session.trajectories[s][:,0] > right)]
            
### OLD STRUCTURE ###

def trajectory_lowpass(trajectories):
    b,a = sig.butter(4,_lowpasscutoff / (_samplerate * 2))
    return sig.filtfilt(b,a,trajectories)

def get_labeled_indices(labels,labelfilter=None):
    if labelfilter is None:
        return range(len(labels))
    return [i for i,l in enumerate(labels) if utils.is_dict_subset(labelfilter,l)]

def get_aligned_slices(trajectories,slices,indices,before=_dabefore,after=_daafter):
    return [slice(s.start + indices[i] - before,s.start + indices[i] + after) for i,s in enumerate(slices) if indices[i] is not None]
    
def get_step_aligned_slices(trajectories,slices,steps,labels,stepindex,labelfilter,before=_dabefore,after=_daafter):
    indices = get_labeled_indices(labels,labelfilter)
    stepindices = procsteps.get_first_step_onsets([steps[i] for i in indices],stepindex)
    return get_aligned_slices(trajectories,[slices[i] for i in indices],stepindices,before,after)
    
def get_step_aligned_speeds(trajectories,slices,steps,labels,stepindex,labelfilter,before=_dabefore,after=_daafter):
    aligned_slices = get_step_aligned_slices(trajectories,slices,steps,labels,stepindex,labelfilter,before,after)
    return get_speed_series(trajectories,aligned_slices)
    
def get_step_aligned_heights(trajectories,slices,steps,labels,stepindex,labelfilter,before=_dabefore,after=_daafter):
    aligned_slices = get_step_aligned_slices(trajectories,slices,steps,labels,stepindex,labelfilter,before,after)
    return get_height_series(trajectories,aligned_slices)
    
def get_step_aligned_horizontal_tips(trajectories,slices,steps,labels,stepindex,labelfilter,before=_dabefore,after=_daafter):
    aligned_slices = get_step_aligned_slices(trajectories,slices,steps,labels,stepindex,labelfilter,before,after)
    return get_horizontal_tip_series(trajectories,aligned_slices)
    
def get_speed_series(trajectories,slices):
    return [np.insert(sigproc.smooth(get_trajectory_speed(trajectories[s,0:2])),0,0) for s in slices]
    
def get_height_series(trajectories,slices):
    return [trajectories[s,1] for s in slices]
    
def get_horizontal_tip_series(trajectories,slices):
    return [trajectories[s,0] for s in slices]
    
def get_session_trajectory(t,i,j,trials=slice(None)):
    return (t.trajectories[i][j],t.slices[i][j][trials],t.videos[i][j],t.steps[i][j][trials],t.labels[i][j][trials])

def load_trajectory_labels(path):
    trajectory_labels = []
    with open(path,'r') as f:
        for line in f:
            trajectory_labels.append(ast.literal_eval(line))
    return trajectory_labels
    
def load_all_trajectory_labels(datafolder):
    return [load_trajectory_labels(path) for path in glob.glob(datafolder + '/*/*/*trajectory_labels.csv')]

def save_trajectory_labels(trajectories):
    for x in trajectories:
        timestamp_path = os.path.splitext(x[2])[0] + '.csv'
        timestamps = np.genfromtxt(timestamp_path,dtype=str)
        datafolder = os.path.split(x[2])[0]
        step_trial_files = [os.path.join(datafolder,r'step%s_trials.csv') % (s) for s in range(1,7)]
        step_trials = np.array([utils.ensure_list(np.genfromtxt(f,dtype=bool)) if os.path.exists(f) else np.array([]) for f in step_trial_files])
        
        left_rewards = utils.ensure_list(np.genfromtxt(os.path.join(datafolder,r'left_rewards.csv'),dtype=str))
        right_rewards = utils.ensure_list(np.genfromtxt(os.path.join(datafolder,r'right_rewards.csv'),dtype=str))
        reward_times = filter(None,utils.flatten(it.izip_longest(left_rewards,right_rewards)))
        
        trajectory_trial_mapping = []
        for trajectory in x[1]:
            candidate_trials = [i+1 for i in range(len(reward_times)) if reward_times[i] < timestamps[trajectory.start]]
            if len(candidate_trials) > 0:
                trajectory_trial_mapping.append(candidate_trials[-1])
            else:
                trajectory_trial_mapping.append(0)
        
        trajectory_labels = []
        for i,trajectory in enumerate(x[1]):
            labels = {}
            trial_number = trajectory_trial_mapping[i]
            step_state = [step_trial[min(trial_number,len(step_trial)-1)] for step_trial in step_trials]
            direction_label = 'left' if x[0][trajectory.start,0] > 640 else 'right'
            stable_crossing_label = 'stable' if np.all(step_state) else 'unstable'
            labels['direction'] = direction_label
            labels['state'] = stable_crossing_label
            trajectory_labels.append(labels)
        
        trajectory_label_path = os.path.join(datafolder,r'Analysis\trajectory_labels.csv')
        np.savetxt(trajectory_label_path,trajectory_labels,fmt='%s')

def save_trajectory_slices(trajectories):
    for x in trajectories:
        timestamp_path = os.path.splitext(x[2])[0] + '.csv'
        timestamps = np.genfromtxt(timestamp_path,dtype=str)
        trajectory_slices = flatten([[timestamps[s.start] + ' WindowOpening',timestamps[s.stop-1] + ' WindowClosing'] for s in x[1]])
        trajectory_slice_path = os.path.join(os.path.split(x[2])[0],r'Analysis\trajectory_slices.csv')
        np.savetxt(trajectory_slice_path,trajectory_slices,fmt='%s')

def iterate_trajectories(t,subjects=None,sessions=None,trials=slice(None)):        
    if subjects is None:
        subjects = range(len(t.trajectories))
    if sessions is None:
        sessions = range(len(t.trajectories[0]))
    
    for i in subjects:
        for j in sessions:
            yield get_session_trajectory(t,i,j,trials)

def pickle_file(path,obj):
    with open(path,'wb') as pickled_file:
        pickle.dump(obj,pickled_file,pickle.HIGHEST_PROTOCOL)

def flatten(l):
    return [item for sublist in l for item in sublist]
    
def load_trajectories(datafolder):
    return [np.genfromtxt(path) for path in glob.glob(datafolder + '/*/*/*trajectories.csv')]
    
def load_trajectory_timestamps(datafolder):
    return [np.genfromtxt(path) for path in glob.glob(datafolder + '/*/*front_video.csv')]
    
def load_slips(datafolder):
    return [np.genfromtxt(path) for path in glob.glob(datafolder + '/*/*/*slip_activity.csv')]
    
def get_trajectory_videos(datafolder):
    globbed = glob.glob(datafolder + '/*/*/*trajectories.csv')
    return [os.path.join(os.path.split(os.path.split(path)[0])[0],'front_video.avi') for path in globbed]

def clump_trajectories(trajectories,crop=[0,1300],minpathlength=100):
    mask = np.ma.masked_outside(trajectories[:,0],crop[0],crop[1])
    clump_slices = np.ma.clump_unmasked(mask)
    return [s for s in clump_slices
    if s.stop - s.start >= minpathlength]

##################### SLICING #################################################
def slice_trajectories(trajectories):
    mask = np.ma.masked_equal(trajectories[:,0],-1)
    return np.ma.clump_unmasked(mask)
    
def get_center_crossings(trajectories,slices,center=640):
    return [s for s in slices if
    (trajectories[s.start,0] < center and trajectories[s.stop-1,0] > center) or
    (trajectories[s.start,0] > center and trajectories[s.stop-1,0] < center)]
    
def crop_slices(trajectories,slices,crop=[200,1000]):
    def test_slice(s):
        return (trajectories[s,0] > crop[0]) & (trajectories[s,0] < crop[1])
    
    def crop_slice(s):
        valid_indices = np.nonzero(test_slice(s))[0]
        min_index = np.min(valid_indices)
        max_index = np.max(valid_indices)
        return slice(s.start+min_index,s.start+max_index+1)
    return [crop_slice(s) for s in slices if np.any(test_slice(s))]

def filter_long_trials(slices,maxduration=600):
    return [s for s in slices if (s.stop-s.start) <= maxduration]
    
def filter_rear_trials(trajectories,slices,rearheight=300):
    return [s for s in slices if not np.any(trajectories[s,1] < rearheight)]
    
def crop_position(trajectories,slices,crop=[200,1000]):
    return [s for s in slices]
        
def flip_slice(s):
    if s.step is None:
        return slice(s.stop-1,s.start-1,-1)
    else:
        return slice(s.stop+1,s.start+1)
        
def normalize_direction(x,edge=1280.):
    return x if x[0] < (edge/2) else edge-x
    
def get_sliced_data(data,slices):
    return [data[s,:] for s in slices]

def clip_data(data,xtip,crop=[200,1000]):
    return np.array(data)[(xtip > crop[0]) & (xtip < crop[1])]
###############################################################################
    
##################### METRICS #################################################
    
def get_average_height(trajectories,slices):
    return [np.mean(trajectories[s,1]) for s in slices]
    
###############################################################################
    
def get_speeds(trajectories,slices):
    return [[max([ln.norm(v) for v in np.diff(trajectories[i][s,0:2],axis=0)]) for s in slices[i]] for i in range(len(trajectories))]
    
def preprocess(trajectories):
    nose = [[t[s,0:2] for s in clump_trajectories(t)] for t in trajectories]
    fnose = flatten(nose)
    return np.array([get_trajectory_features(t) for t in fnose])
    
def load_preprocess(datafolder):
    trajectories = load_trajectories(datafolder)
    return preprocess(trajectories)
    
def distance_traveled(trajectory):
    deltas = np.diff(trajectory,axis=0)
    return np.sum([ln.norm(v) for v in deltas])
    
def min_height(trajectory):
    return np.min(trajectory,axis=0)[1]
    
def max_height(trajectory):
    return np.max(trajectory,axis=0)[1]
    
def max_delta(trajectory):
    deltas = np.diff(trajectory,axis=0)
    return np.max([ln.norm(v) for v in deltas])
    
def get_speed_normalizer(speeds,q):
    distribution = np.concatenate([utils.flatten(s) for s in speeds])
    return np.percentile(distribution,q)
    
def get_trajectory_speed(trajectory):
    displacement = np.diff(trajectory,axis=0)
    return np.array([ln.norm(v) for v in displacement])
    
def preprocess_speed_features(trajectories,slices,speeds,normalizer=1):
    return np.array([get_speed_features(trajectories[s,0:2],sp,normalizer) for s,sp in it.izip(slices,speeds)])
    
def get_speed_features(trajectory,speed,normalizer=1,left=425,right=850):
    center_speed = np.average([s / normalizer 
                               for s,p in it.izip(speed,it.islice(trajectory,1,None))
                               if p[0] > left and p[0] < right])
    edge_speed = np.average([s / normalizer
                               for s,p in it.izip(speed,it.islice(trajectory,1,None))
                               if p[0] <= left or p[0] >= right])
    return (center_speed,edge_speed)
    
def get_trajectory_features(trajectory):
    displacement = np.diff(trajectory,axis=0)
    speed = [ln.norm(v) for v in displacement]
    
    distance = np.sum(speed)
#    max_speed = np.max(speed)
#    min_speed = np.min(speed)
    avg_speed = np.average(speed)
    std_speed = np.std(speed)
#    min_height = np.min(trajectory,axis=0)[1]
#    max_height = np.max(trajectory,axis=0)[1]
    avg_height = np.average(trajectory,axis=0)[1]
    std_height = np.std(trajectory,axis=0)[1]
    avg_progression = (np.average(trajectory,axis=0)[0] - 200) / 800
    if trajectory[0,0] > 600:
        avg_progression = 1 - avg_progression
    return [distance,avg_speed,std_speed,avg_height,std_height,avg_progression]
    
def build_raw_trajectories(datafolder):
    trajectories = load_trajectories(datafolder)
    timestamps = load_trajectory_timestamps(datafolder)
    slices = [clump_trajectories(t) for t in trajectories]
    videos = get_trajectory_videos(datafolder)
    speeds = get_speeds(trajectories,slices)
    trajectory_structure = zip(trajectories,slices,video)
    save_trajectory_labels(trajectory_structure)
    save_trajectory_slices(trajectory_structure)
    datafolders = [os.path.join(datafolder,folder) for folder in os.listdir(datafolder)]
    shuttling_analysis.analysis_pipeline(datafolders, False)
    labels = load_all_trajectory_labels(datafolder)
    steps = procsteps.load_stepactivities(datafolder)
    slips = load_slips(datafolder)
    return load_data.session(
    trajectories=trajectories,
    timestamps=timestamps,
    slices=slices,
    videos=videos,
    speeds=speeds,
    labels=labels,
    steps=steps,
    slips=slips)
    
def update_trajectory_structure(t):
    return [[load_data.session(
    trajectories=t.trajectories[i][j],
    time=t.timestamps[i][j],
    slices=t.slices[i][j],
    video=t.videos[i][j],
    speeds=t.speeds[i][j],
    labels=t.labels[i][j],
    steps=t.steps[i][j],
    slips=t.slips[i][j])
    for j,s in enumerate(a)] for i,a in enumerate(t.trajectories)]

def swap_head_tail(trajectories):
    trajectories[:,[0,1,2,3]] = trajectories[:,[2,3,0,1]]
        
#def remap_experiment_structure(experiment,slips):
#    return [[load_data.session(
#    trajectories=s.trajectories,
#    time=s.time,
#    slices=s.slices,
#    video=s.video,
#    speeds=s.speeds,
#    labels=s.labels,
#    steps=s.steps,
#    slips=[ss[sl] for sl in s.slices]
#    ) for s,ss in it.izip(a,sa)] for a,sa in it.izip(experiment,slips)]
        
def remap_experiment_structure(experiment):
    return [[load_data.session(
    trajectories=s.trajectories,
    time=s.time,
    slices=s.slices,
    video=s.video,
    speeds=s.speeds,
    labels=s.labels,
    steps=s.steps,
    slips=s.slips
    ) for s in a] for a in experiment]
        
def revert_experiment_structure(experiment):
    return load_data.session(
    trajectories=[[s.trajectories for s in a] for a in experiment],
    timestamps=[[s.timestamps for s in a] for a in experiment],
    slices=[[s.slices for s in a] for a in experiment],
    videos=[[s.videos for s in a] for a in experiment],
    speeds=[[s.speeds for s in a] for a in experiment],
    labels=[[s.labels for s in a] for a in experiment],
    steps=[[s.steps for s in a] for a in experiment])
    
def merge_all_trajectories(ts):
    return load_data.session(
    trajectories=[a.trajectories for a in ts],
    timestamps=[a.timestamps for a in ts],
    slices=[a.slices for a in ts],
    video=[a.video for a in ts],
    speeds=[a.speeds for a in ts],
    labels=[a.labels for a in ts],
    steps=[a.steps for a in ts],
    slips=[a.slips for a in ts])
    
def merge_trajectories(t,t2,offset=0):
    for i in range(len(t2)):
        t.trajectories[offset+i] = t2[i].trajectories
        t.timestamps[offset+i] = t2[i].timestamps
        t.slices[offset+i] = t2[i].slices
        t.video[offset+i] = t2[i].video
        t.speeds[offset+i] = t2[i].speeds
        t.labels[offset+i] = t2[i].labels
        t.steps[offset+i] = t2[i].steps