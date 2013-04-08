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

# for shuttling assay number 1 !!!
#roi_step_centers = [154,292,452,626.5,784,949]
roi_step_centers = [114,281,420,580,750,905,1056,1200]
interpolation_range = range(50,1250)
default_crop = [0,1280]

def update_mean_series(n,mean,series):
    n = n + 1
    if n == 1:
        mean = np.array(series)
    else:
        for i in range(len(mean)):
            if i >= len(series):
                break
            
            delta = series[i] - mean[i]
            mean[i] = mean[i] + delta/n
    return n,mean

def get_time_video_pos_msec(session,time):
    return (time - session.start_time).total_seconds() * 1000.0

def get_trial_video_pos_msec(session,trial,frame=0):
    return get_time_video_pos_msec(session, dateutil.parser.parse(session.trial_time[trial][frame]))

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
    
def get_boundary_indices(data):
    return np.cumsum([len(data[i]) for i in range(len(data)-1)])
    
def get_directionless_tip_trajectory(xtip,ytip,cdirection):
    #valid_indices = [i for i,x in enumerate(xtip) if x > 0]
    #valid_indices = utils.consecutive_elements(valid_indices)
    #valid_indices = utils.flatten(valid_indices[slice(len(valid_indices),-2,-1)])
    #valid_indices = [i for i in valid_indices if xtip[i] >= 50 and xtip[i] <= 1020]
    
    valid_indices = [i for i,x in enumerate(xtip) if x > 0]
    valid_indices = utils.consecutive_elements(valid_indices)
    valid_indices = max(valid_indices,key=len)
    
    rdir = xtip[valid_indices[0]] > 600
    if rdir:
        left_side = utils.find_lt(xtip[valid_indices],1020)
        right_side = utils.find_lt(xtip[valid_indices],50)
    else:
        left_side = utils.find_gt(xtip[valid_indices],50)
        right_side = utils.find_gt(xtip[valid_indices],1020)
    
    valid_indices = valid_indices[slice(left_side,right_side)]
    
    #valid_indices = [i for i,x in enumerate(xtip) if x >= 50 and x <= 1020]
    #valid_indices = utils.consecutive_elements(valid_indices)
    #valid_indices = max(valid_indices,key=len)
    
    x = np.array([xtip[ind] for ind in valid_indices])
    y = np.array([ytip[ind] for ind in valid_indices])
    vbounds_exceeded = sum((y < 600) | (y > 800))
    return (x,y,vbounds_exceeded == 0 and len(xtip) > 0 and xtip[0] < 0,rdir)
    
def get_spatial_variable_interpolation(x,y,interprange):
    sortedindices = np.argsort(x[1:])
    values = zip(x[sortedindices+1],y[sortedindices])
    values = [(g[0],np.average([v[1] for v in g[1]])) for g in itertools.groupby(values,key=lambda p:p[0])]
    [xvals,yvals] = zip(*values)
    return np.interp(interprange,xvals,yvals)
    
def get_spatial_tip_height_trial(session,i):
    xtip = np.array(session.tip_horizontal[i])
    ytip = np.array(session.tip_vertical[i])
    return get_spatial_variable_interpolation(xtip,ytip,interpolation_range)
    
def get_tip_horizontal_speed_trial(session,i):
    xtip = np.array(session.tip_horizontal[i])
    xdisplacement = np.diff(xtip)
    speed = np.sqrt(xdisplacement * xdisplacement)
    return get_spatial_variable_interpolation(xtip,speed,interpolation_range)

def get_tip_trajectory_trial(session,i,crop=[0,1280]):
    xtip = np.array(session.tip_horizontal[i])
    ytip = np.array(session.tip_vertical[i])
    rdir = session.crossing_direction[i]
    valid_samples = (xtip > crop[0]) & (xtip < crop[1])
#    return get_directionless_tip_trajectory(xtip,ytip,rdir)
    return xtip[valid_samples],ytip[valid_samples],rdir
    
def get_tip_spatial_speed_trial(session,i):
    x,y,decision = get_tip_trajectory_trial(session,i)
    xspeed = np.diff(x)
    yspeed = np.diff(y)
    speed = np.sqrt(xspeed * xspeed + yspeed * yspeed)
    sortedindices = np.argsort(x[1:])
    values = zip(x[sortedindices+1],speed[sortedindices])
    values = [(g[0],np.average([v[1] for v in g[1]])) for g in itertools.groupby(values,key=lambda p:p[0])]
    
    try:
        [xvals,svals] = zip(*values)
    
        spline = UnivariateSpline(xvals,svals)
        xs = interpolation_range
        speed_spline = spline(xs)
        return speed_spline,speed,decision
    except Exception:
        return None,speed,False
        
def get_clipped_trial_variable(session,i,variable,crop=default_crop):
    xtip = np.array(session.tip_horizontal[i])
    valid_samples = (xtip > crop[0]) & (xtip < crop[1])
    return np.array(variable)[valid_samples]
    
def get_clipped_trajectories(session):
    return [[x for x in trajectory if x < 1077] for trajectory in session.tip_horizontal_path]

def get_crossing_expansion(session,trial_variable):
    trial_expansions = np.bincount(session.crossing_trial_mapping)
    return utils.flatten([[x]*c for x,c in itertools.izip_longest(trial_variable,trial_expansions,fillvalue=trial_expansions[len(trial_expansions)-1])])

def get_first_crossings_in_trial(session):
    return np.insert(np.diff(session.crossing_trial_mapping),0,1) > 0
    
def get_first_crossing_trial_times(session,valid_trials=None):
    first_crossings_in_trial = get_first_crossings_in_trial(session)
    if valid_trials is not None:
        valid_trials = get_crossing_expansion(session,valid_trials)
        first_crossings_in_trial &= valid_trials
        
    return [(session.reward_times[session.crossing_trial_mapping[i]] - dateutil.parser.parse(session.trial_time[i][path[0]])).total_seconds()
    for i,path in enumerate(np.array(session.tip_horizontal_path_indices)) if first_crossings_in_trial[i]
    if session.crossing_trial_mapping[i] < len(session.reward_times)]
    
# Gets an array of the average height of the nose tip for each crossing
# Outputs a tuple/list of [trial_variable,trial_indices,numberoftrials]
# This allows for plotting data end-to-end and retain valid offsets for different colorings
def get_average_crossing_tip_height(session,valid_trials=None,crop=default_crop):
    average_height = np.array([np.mean(get_clipped_trial_variable(session,i,trial,crop)) for i,trial in enumerate(session.tip_vertical)])
    if(valid_trials is not None):
        valid_trials = get_crossing_expansion(session,valid_trials)
        zipped_trials = map(np.array, zip(*[(i,x) for i,(x,v) in enumerate(zip(average_height,valid_trials)) if v]))
        if zipped_trials != []:
            return zipped_trials + [len(average_height)]
        else:
            return [np.array([]),np.array([]),len(average_height)]
#        average_height = [x for x,v in zip(average_height,valid_trials) if v]
    return [np.array(range(len(average_height))),average_height,len(average_height)]
    
# Gets an array of the average height of the nose tip for each crossing
# Outputs a tuple/list of [trial_variable,trial_indices,numberoftrials]
# This allows for plotting data end-to-end and retain valid offsets for different colorings
def get_average_crossing_tip_speed(session,valid_trials=None,crop=default_crop):
    average_speeds = np.array([np.mean(np.sqrt(np.power(np.diff(get_clipped_trial_variable(session,i,trialx,crop)),2) + np.power(np.diff(get_clipped_trial_variable(session,i,trialy,crop)),2))) for i,(trialx,trialy) in enumerate(zip(session.tip_horizontal,session.tip_vertical))])
    if(valid_trials is not None):
        valid_trials = get_crossing_expansion(session,valid_trials)
        zipped_trials = map(np.array, zip(*[(i,x) for i,(x,v) in enumerate(zip(average_speeds,valid_trials)) if v]))
        if zipped_trials != []:
            return zipped_trials + [len(average_speeds)]
        else:
            return [np.array([]),np.array([]),len(average_speeds)]        
#        average_speeds = [x for x,v in zip(average_speeds,valid_trials) if v]
    return [np.array(range(len(average_speeds))),average_speeds,len(average_speeds)]
  
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
    session_type = 'merged')
    
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

# in dev: split sessions based on selection criterion (either selection_value or not selection_value)
def split_sessions(sessions, selection_criterion='light_trial', selection_value=1):
    result = []
   # for session in sessions:
        
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
    
    left = [times[i] for i in session.left_crossings]
    right = [times[i] for i in session.right_crossings]
#    left = [times[i] for i,centroid in enumerate(centroids) if len(centroid) > 0 and centroid[0] >= 0 and centroid[0] < roi_step_centers[stepindex]]
#    right = [times[i] for i,centroid in enumerate(centroids) if len(centroid) > 0 and centroid[0] >= 0 and centroid[0] > roi_step_centers[stepindex]]
    return times,centroids,left,right
    
def step_front(session,stepindex):
    sti = [(mlab.find(session.steps[stepindex][i])[slice(1)],i) for i in session.right_crossings]
    return [session.trial_time[i[1]][i[0]] for i in sti if len(i[0]) > 0 and session.tip_horizontal[i[1]][i[0]] < 900] 
    
def step_tip_distribution(session,stepindex):
    sti = [(mlab.find(session.steps[stepindex][i])[slice(1)],i) for i in session.right_crossings]
    return [session.tip_horizontal[i[1]][i[0]] for i in sti if len(i[0]) > 0]
    
def step_probabilities(session):
    return [1 - (len([1 for trial in step if sum(trial) > 0]) / float(len(session.tip_horizontal))) for step in session.steps]
    
def manipulated_step_probabilities(session):
    trials = [i for i,trial in enumerate(session.crossing_trial_mapping) if session.manipulation_trials[trial]]
    return conditional_step_probabilities(session,trials)
    
def conditional_step_probabilities(session,trials):
    return [1 - (len([1 for i in trials if sum(step[i]) > 0]) / float(len(trials))) for step in session.steps]
    
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