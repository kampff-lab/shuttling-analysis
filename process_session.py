# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import cv
import itertools
import matplotlib.mlab as mlab
import numpy as np
import dateutil
import scipy.cluster.hierarchy as hcl
import parse_session
import analysis_utilities as utils
import image_processing as imgproc
from scipy.interpolate import UnivariateSpline
import bisect

# for shuttling assay number 1 !!!
roi_step_centers = [154,292,452,626.5,784,949]

def make_step_means(session):
    for i in range(len(session.steps)):
        for category in ['Left', 'Right']:
            path = r'Steps\Step%s\%s' % (i, category)
            output = r'%s\step_average.png' % path
            images = imgproc.load_image_folder(path,iscolor=False)
            mean = imgproc.average_image_list(images)
            cv.SaveImage(output, mean)
            del images
            
def make_step_maxintensity(session):
    for i in range(len(session.steps)):
        for category in ['Left', 'Right']:
            path = r'Steps\Step%s\%s' % (i, category)
            output = r'%s\step_average.png' % path
            images = imgproc.load_image_folder(path,iscolor=False)
            maxintensity = imgproc.max_image_list(images)
            cv.SaveImage(output, maxintensity)
            del images

def make_step_times(session):
    for i in range(len(session.steps)):
        (times,centroids,left,right) = step_times(session,i)
        left_timestamps = utils.flatten(left)
        right_timestamps = utils.flatten(right)
        
        #step_timestamps = utils.flatten(step_times(session,i))
        np.savetxt('step%s_times_left.csv' % (i),left_timestamps,'%s')
        np.savetxt('step%s_times_right.csv' % (i),right_timestamps,'%s')

def setup_weighted_image_mean(session,timepath,imagepath):
    weights = []
    filenames = []
    for path in session.path:
        image_file = path + r"/" + imagepath
        if os.path.exists(image_file):
            times = np.genfromtxt(path + r"/" + timepath,dtype=str)
            weights.append(float(len(times)))
            filenames.append(image_file)
    weights = weights / sum(weights)
    return (weights,filenames)

def weighted_image_mean(weights,filenames,resultpath):
    result = None
    for i in range(len(weights)):
        filename = filenames[i]
        image = cv.LoadImage(filename,False)
        cv.ConvertScale(image,image,weights[i])
        if result is None:
            result = image
        else:
            cv.Add(image,result,result)
    cv.SaveImage(resultpath,result)
    
def get_directionless_tip_trajectory(xtip,ytip,cdirection):
    #valid_indices = [i for i,x in enumerate(xtip) if x > 0]
    #valid_indices = utils.consecutive_elements(valid_indices)
    #valid_indices = utils.flatten(valid_indices[slice(len(valid_indices),-2,-1)])
    #valid_indices = [i for i in valid_indices if xtip[i] >= 50 and xtip[i] <= 1020]
    
    valid_indices = [i for i,x in enumerate(xtip) if x > 0]
    valid_indices = utils.consecutive_elements(valid_indices)
    valid_indices = max(valid_indices,key=len)
    
    cdirection = xtip[valid_indices[0]] > 600
    if cdirection:
        left_side = utils.find_lt(xtip[valid_indices],1020)
        right_side = utils.find_lt(xtip[valid_indices],50)
    else:
        left_side = utils.find_gt(xtip[valid_indices],50)
        right_side = utils.find_gt(xtip[valid_indices],1020)
    
    valid_indices = valid_indices[slice(left_side,right_side)]
    
    #valid_indices = [i for i,x in enumerate(xtip) if x >= 50 and x <= 1020]
    #valid_indices = utils.consecutive_elements(valid_indices)
    #valid_indices = max(valid_indices,key=len)
    
    x = np.array([cdirection and (1070 + xtip[ind] * -1) or xtip[ind] for ind in valid_indices])
    y = np.array([ytip[ind] for ind in valid_indices])
    vbounds_exceeded = sum((y < 600) | (y > 800))
    return (x,y,vbounds_exceeded == 0 and len(xtip) > 0 and xtip[0] < 0)

def get_tip_trajectory_trial(session,i):
    xtip = np.array(session.tip_horizontal[i])
    ytip = np.array(session.tip_vertical[i])
    cdirection = session.crossing_direction[i]
    return get_directionless_tip_trajectory(xtip,ytip,cdirection)
    
def get_tip_spatial_speed_trial(session,i):
    x,y,decision = get_tip_trajectory_trial(session,i)
    xspeed = np.diff(x)
    yspeed = np.diff(y)
    speed = np.sqrt(xspeed * xspeed + yspeed * yspeed)
    sortedindices = np.argsort(x[1:])
    values = zip(x[sortedindices+1],speed[sortedindices])
    values = [(g[0],np.average([v[1] for v in g[1]])) for g in itertools.groupby(values,key=lambda p:p[0])]
    [xvals,svals] = zip(*values)
    
    spline = UnivariateSpline(xvals,svals)
    xs = range(100,1000)
    speed_spline = spline(xs)
    return speed_spline,speed,decision
    
def get_clipped_trajectories(session):
    return [[x for x in trajectory if x < 1077] for trajectory in session.tip_horizontal_path]    
    
def get_trial_times(session):
    valid_trials = np.insert(np.diff(session.crossing_trial_mapping),0,1)
    return [(session.reward_times[session.crossing_trial_mapping[i]] - dateutil.parser.parse(session.trial_time[i][path[0]])).total_seconds() for i,path in enumerate(np.array(session.tip_horizontal_path_indices)[valid_trials]) if session.crossing_trial_mapping[i] < len(session.reward_times)]
  
def merge_sessions(name,sessions):
    result = parse_session.session(
    name = name, path = utils.flatten([s.path for s in sessions]),
    mean = utils.flatten([s.mean for s in sessions if s.mean is not None]),
    tip_horizontal = utils.flatten([s.tip_horizontal for s in sessions if s.tip_horizontal is not None]),
    tip_horizontal_path = utils.flatten([s.tip_horizontal_path for s in sessions if s.tip_horizontal_path is not None]),
    tip_vertical = utils.flatten([s.tip_vertical for s in sessions if s.tip_vertical is not None]),
    crossing_direction = utils.flatten([s.crossing_direction for s in sessions if s.crossing_direction is not None]),
    step_activity = [], steps = [],
    left_crossings = [],
    right_crossings = [],
    merged_sessions = sessions,
    session_type = 'merge')
    
    offset = 0
    for s in sessions:
        if s.left_crossings is None:
            continue
        result.left_crossings.append(np.array(s.left_crossings) + offset)
        offset = offset + len(s.mean)
    result.left_crossings = utils.flatten(result.left_crossings)
    
    if s.steps is not None:
        result.steps = [utils.flatten([s.steps[i] for s in sessions if s.steps]) for i in range(len(sessions[0].steps))]
    return result

def index_distribution(boolean_trials,s=slice(None)):
    return utils.flatten_slice([
    [i for i in range(len(boolean_trials[trial]))
    if boolean_trials[trial][i]]
    for trial in range(len(boolean_trials))],s)

#def step_indices(boolean_trials,s=slice(None)):
#    indices = [[i for i in range(len(boolean_trials[trial]))
#    if boolean_trials[trial][i]]
#    for trial in range(len(boolean_trials))]
#    return [item[s] for item in indices]
    
def get_step_aligned_data(data,session,stepindex,before=0,after=0,padinvalid=True):
    (step_centroids,step_left,step_right) = step_indices(session,stepindex)
    left = utils.get_aligned_data(data,step_left,before,after,padinvalid)
    right = utils.get_aligned_data(data,step_right,before,after,padinvalid)
    return left,right
    
def first_step_indices(session,stepindex):
    return [[i for i,x in enumerate(trial) if x > 100000][slice(1)] for trial in session.step_activity[stepindex]]
    
def step_indices(session,stepindex):
    sti = first_step_indices(session,stepindex)
    centroids = [len(sti[i]) > 0 and [trajectory[sti[i][0]]] or [] for i,trajectory in enumerate(session.centroid_x)]
    left = [len(centroid) > 0 and centroid[0] >= 0 and centroid[0] < roi_step_centers[stepindex] and sti[i][0] or -1 for i,centroid in enumerate(centroids)]
    right = [len(centroid) > 0 and centroid[0] >= 0 and centroid[0] > roi_step_centers[stepindex] and sti[i][0] or -1 for i,centroid in enumerate(centroids)]
    return centroids,left,right

def step_times(session,stepindex):
    sti = first_step_indices(session,stepindex)
    times = [len(sti[i]) > 0 and [trial[sti[i][0]]] or [] for i,trial in enumerate(session.trial_time)]
    centroids = [len(sti[i]) > 0 and [trajectory[sti[i][0]]] or [] for i,trajectory in enumerate(session.centroid_x)]
    #direction = [(len(centroid) > 0 and centroid[0] >= 0) and [centroid[0] < roi_step_centers[stepindex]] or [] for i,centroid in enumerate(centroids)]
    left = [times[i] for i,centroid in enumerate(centroids) if len(centroid) > 0 and centroid[0] >= 0 and centroid[0] < roi_step_centers[stepindex]]
    right = [times[i] for i,centroid in enumerate(centroids) if len(centroid) > 0 and centroid[0] >= 0 and centroid[0] > roi_step_centers[stepindex]]
    return times,centroids,left,right
    
def step_front(session,stepindex):
    sti = [(mlab.find(session.steps[stepindex][i])[slice(1)],i) for i in session.right_crossings]
    return [session.trial_time[i[1]][i[0]] for i in sti if len(i[0]) > 0 and session.tip_horizontal[i[1]][i[0]] < 900] 
    
def step_tip_distribution(session,stepindex):
    sti = [(mlab.find(session.steps[stepindex][i])[slice(1)],i) for i in session.right_crossings]
    return [session.tip_horizontal[i[1]][i[0]] for i in sti if len(i[0]) > 0]
    
def step_probabilities(session):
    return [len([1 for trial in step if sum(trial) > 0]) / float(len(session.tip_horizontal)) for step in session.steps]
    
def manipulated_step_probabilities(session):
    trials = [i for i,trial in enumerate(session.crossing_trial_mapping) if session.manipulation_trials[trial]]
    return conditional_step_probabilities(session,trials)
    
def conditional_step_probabilities(session,trials):
    return [len([1 for i in trials if sum(step[i]) > 0]) / float(len(trials)) for step in session.steps]
    
def get_tip_horizontal_speed_trials(trials,trial_slice=slice(None)):
    return [np.diff(trial)[trial_slice] for trial in trials]
    
def get_spatial_speed_distribution(trials):
    spatial_distribution = filter(lambda x:x < 1077,utils.flatten(trials))
    speed_distribution = get_tip_horizontal_speed_trials(trials)
    hst = np.histogram(spatial_distribution,100)
    bins = hst[1]
    bin_indices = [np.digitize(progression,bins) for progression in trials]
    spatial_speed = np.zeros(len(bins))
    spatial_samples = np.zeros(len(bins))
    for i in xrange(len(speed_distribution)):
        speed_values = speed_distribution[i]
        speed_indices = bin_indices[i]
        for j in xrange(len(speed_values)):
            if speed_indices[j] < len(bins):
                spatial_speed[speed_indices[j]] += speed_values[j]
                spatial_samples[speed_indices[j]] += 1
    return (hst,spatial_speed,spatial_samples)
    
def step_posture_clusters(session,stepindex,keep_image_list=True):
    images = utils.flatten([imgproc.load_image_folder(path + r'/Steps/Step%s' % (stepindex)) for path in session.path])
    distances = imgproc.pixel_distance_matrix(images)
    clusters = hcl.complete(distances)    
    if not keep_image_list:
        del images
        images = None
    return (distances,clusters,images)
    
def split_clusters(data,fclusters):
    result = [[] for i in xrange(max(fclusters))]    
    for i in xrange(len(data)):
        result[fclusters[i]-1].append(data[i])
    return result