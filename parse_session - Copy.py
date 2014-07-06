# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import os
import glob
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
    frame_time = np.genfromtxt(r'..\front_video.csv',dtype=str,usecols=0)
    start_time = dateutil.parser.parse(frame_time[0])
    
    # Default member placeholders
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
    step_times = None
    light_trials = None
    crossing_light_condition = None
    left_poke = None
    right_poke = None
    front_activity = None
    crossing_labels = None
    step_trials = None
    
    if analysis:
        if os.path.exists(r'..\front_activity.csv'):
            front_activity = np.genfromtxt(r'..\front_activity.csv')
        
        if os.path.exists(r'..\left_poke.csv'):
            left_poke = [np.genfromtxt(r'..\left_poke.csv',usecols=0),np.genfromtxt(r'..\left_poke.csv',usecols=1,dtype=str)]
            right_poke = [np.genfromtxt(r'..\right_poke.csv',usecols=0),np.genfromtxt(r'..\right_poke.csv',usecols=1,dtype=str)]
        
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
                
        # extract light trial pattern and tile it to be as long as the number of trials
        if os.path.exists(r'..\light_trials.csv'):
            light_trials = np.genfromtxt(r'..\light_trials.csv',dtype=bool)
            light_trials = np.tile(light_trials, (len(reward_times) / len(light_trials) + 1))
            light_trials = light_trials[0:len(reward_times)]
        
            light_trial_crossing_count = np.bincount(crossing_trial_mapping)
            crossing_light_condition = utils.flatten([[x]*c for x,c in zip(light_trials,light_trial_crossing_count)])
        else:
            light_trials = None
            crossing_light_condition = None
        
        stepfiles = [f for f in glob.glob("step*.csv") if len(f) <= 9]
        step_activity = [utils.loadfromcsv(step) for step in stepfiles]
        step_threshold = [[np.array([x > 100000 and 1 or 0 for x in trial]) for trial in step] for step in step_activity]
        steps = [[np.insert(np.diff(trial),0,0) > 0 for trial in step] for step in step_threshold]
        step_times_files = ['step%s_times.csv' % (s) for s in range(len(stepfiles))]
        step_times = [utils.ensure_list(np.genfromtxt(f,dtype=str)) if os.path.exists(f) else np.array([]) for f in step_times_files]
        step_trial_files = [r'..\step%s_trials.csv' % (s) for s in range(1,7)]
        step_trials = np.array([utils.ensure_list(np.genfromtxt(f,dtype=bool)) if os.path.exists(f) else np.array([]) for f in step_trial_files])
        
        tip_horizontal_path = [[x for x in trial if x >= 0] for trial in tip_horizontal]
        tip_vertical_path = [[x for x in trial if x >= 0] for trial in tip_vertical]
        tip_horizontal_path_indices = [[i for i,x in enumerate(trial) if x >= 0] for trial in tip_horizontal];
        
        crossing_labels = []
        for i in range(len(trial_time)):
            labels = {}
            trial_number = crossing_trial_mapping[i]
            step_state = [step_trial[min(trial_number,len(step_trial)-1)] for step_trial in step_trials]
            direction_label = 'left' if tip_horizontal_path[i][0] > 640 else 'right'
            steady_crossing_label = 'steady' if tip_horizontal[i][0] < 0 and tip_horizontal[i][-1] < 0 else 'exploratory'
            stable_crossing_label = 'stable' if np.all(step_state) else 'unstable'
            labels['direction'] = direction_label
            labels['type'] = steady_crossing_label
            labels['state'] = stable_crossing_label
            crossing_labels.append(labels)
        
        crossing_direction = [x[0] > 640 for x in tip_horizontal_path]
        left_crossings = [i for i,x in enumerate(crossing_direction) if x]
        right_crossings = [i for i,x in enumerate(crossing_direction) if not x]
        for i in left_crossings:
            for s in range(len(steps) / 2):
                tmp = steps[s][i]
                steps[s][i] = steps[len(steps)-1-s][i]
                steps[len(steps)-1-s][i] = tmp
#            for j in range(len(tip_horizontal_path[i])):
#                tip_horizontal_path[i][j] = 1078 + (tip_horizontal_path[i][j] * -1)

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
    if len(reward_times) > 0:
        inter_reward_intervals = np.insert(inter_reward_intervals,0,reward_times[0] - start_time)

    os.chdir(cwd)
    return session(
    path=[path],
    name=name,
    mean=mean,
    front_activity=front_activity,
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
    frame_time=frame_time,
    trial_time=trial_time,
    start_time=start_time,
    left_rewards=left_rewards,
    right_rewards=right_rewards,
    reward_times=reward_times,
    inter_reward_intervals=inter_reward_intervals,
    crossing_trial_mapping=crossing_trial_mapping,
    manipulation_trials=manipulation_trials,
    session_type=session_type,
    crossing_labels=crossing_labels,
    step_trials=step_trials,
    light_trials=light_trials,
    crossing_light_condition=crossing_light_condition,
    left_poke=left_poke,
    right_poke=right_poke)