# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import numpy as np
import itertools
import dateutil
import analysis_utilities as utils

class session(object):
  def __init__(self, **kwargs): self.__dict__ = kwargs
  def __eq__(self, r2): return self.__dict__ == r2.__dict__
  def __ne__(self, r2): return self.__dict__ != r2.__dict__
  
def trim_progression_path(progression):
    finish_index = [i for i in xrange(len(progression)) if progression[i] >= 1077]
    if len(finish_index) > 0:
        return progression[0:finish_index[0]]
    else:
        return progression
  
def parse_session(path,name,analysis=True):
    cwd = os.getcwd()
    os.chdir(path)
    start_time = None
    left_rewards = utils.ensure_list(np.genfromtxt(r'..\left_rewards.csv',dtype=str))
    right_rewards = utils.ensure_list(np.genfromtxt(r'..\right_rewards.csv',dtype=str))
    reward_times = filter(None,utils.flatten(itertools.izip_longest(left_rewards,right_rewards)))
    with open(r'..\front_video.csv') as front_video:
        start_time = next((dateutil.parser.parse(str.split(line)[0]) for line in front_video),None)
        
    if analysis:
        mean = utils.loadfromcsv('mean.csv')
        centroid_x = utils.loadfromcsv('centroid_x.csv')
        centroid_y = utils.loadfromcsv('centroid_y.csv')
        tip_horizontal = utils.loadfromcsv('tip_horizontal.csv')
        tip_vertical = utils.loadfromcsv('tip_vertical.csv')
        trial_time = utils.loadfromcsv('trial_time.csv',lambda x:str(x))
        crossing_trial_mapping = []
        for crossing in trial_time:
            candidate_trials = [i+1 for i in range(len(reward_times)) if reward_times[i] < crossing[0]]
            if len(candidate_trials) > 0:
                crossing_trial_mapping.append(candidate_trials[-1])
            else:
                crossing_trial_mapping.append(0)
        
        stepfiles = ['step%s.csv' % (s) for s in range(6)]
        step_activity = [utils.loadfromcsv(step) for step in stepfiles]
        step_threshold = [[np.array([x > 100000 and 1 or 0 for x in trial]) for trial in step] for step in step_activity]
        steps = [[np.insert(np.diff(trial),0,0) > 0 for trial in step] for step in step_threshold]
        step_times = [utils.ensure_list(np.genfromtxt('step%s_times.csv' % (s),dtype=str)) for s in range(6)]
        
        tip_horizontal_path = [[x for x in trial if x >= 0] for trial in tip_horizontal]
        tip_vertical_path = [[x for x in trial if x >= 0] for trial in tip_vertical]
        tip_horizontal_path_indices = [[i for i,x in enumerate(trial) if x >= 0] for trial in tip_horizontal];
        crossing_direction = [x[0] > 600 for x in tip_horizontal_path]
        left_crossings = [i for i,x in enumerate(crossing_direction) if x]
        right_crossings = [i for i,x in enumerate(crossing_direction) if not x]
        for i in left_crossings:
            for s in range(len(steps) / 2):
                tmp = steps[s][i]
                steps[s][i] = steps[len(steps)-1-s][i]
                steps[len(steps)-1-s][i] = tmp
            for j in range(len(tip_horizontal_path[i])):
                tip_horizontal_path[i][j] = 1078 + (tip_horizontal_path[i][j] * -1)
#        tip_horizontal_path = [trim_progression_path(trial) for trial in tip_horizontal_path]
                
#        stepframefiles = ['Steps\Step%s' % (s) for s in range(6)]
#        step_analysis = []
#        for f in stepframefiles:
#            images = load_image_folder(f)
#            distances = pixel_distance_matrix(images)
#            clusters = hcl.complete(distances)
#            del images
#            step_analysis.append((distances, clusters))
    else:
        mean = None
        centroid_x = None
        centroid_y = None
        tip_horizontal = None
        tip_vertical = None
        tip_horizontal_path = None
        tip_horizontal_path_indices = None
        tip_vertical_path = None
        step_activity = None
        steps = None
        left_crossings = None
        right_crossings = None
        crossing_direction = None
        trial_time = None
        crossing_trial_mapping = None

    if os.path.exists(r'..\left_trials.csv'):
        left_trials = np.genfromtxt(r'..\left_trials.csv',dtype=bool)
        right_trials = np.genfromtxt(r'..\right_trials.csv',dtype=bool)
        manipulation_trials = utils.flatten(zip(left_trials,right_trials))
        session_type = 'manipulation'
    else:
        manipulation_trials = None
        session_type = 'stable'
    
    reward_times = [dateutil.parser.parse(time) for time in reward_times]
    inter_reward_intervals = np.diff(reward_times)

    os.chdir(cwd)
    return session(
    path=[path],
    name=name,
    mean=mean,
    centroid_x=centroid_x,
    centroid_y=centroid_y,
    tip_horizontal=tip_horizontal,
    tip_vertical=tip_vertical,
    tip_horizontal_path=tip_horizontal_path,
    tip_horizontal_path_indices=tip_horizontal_path_indices,
    tip_vertical_path=tip_vertical_path,
    step_activity=step_activity,
    steps=steps,
    step_times=step_times,
    crossing_direction=crossing_direction,
    left_crossings=left_crossings,
    right_crossings=right_crossings,
    trial_time=trial_time,
    start_time=start_time,
    left_rewards=left_rewards,
    right_rewards=right_rewards,
    reward_times=reward_times,
    inter_reward_intervals=inter_reward_intervals,
    crossing_trial_mapping=crossing_trial_mapping,
    manipulation_trials=manipulation_trials,
    session_type=session_type)