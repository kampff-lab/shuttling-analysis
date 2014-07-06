# -*- coding: utf-8 -*-
"""
Created on Tue May 28 23:10:53 2013

@author: gonca_000
"""

import load_data
import plot_session
import matplotlib.pyplot as plt

mc_lesionsham_dataset = [r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_20.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_21.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_22.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_23.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_24.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_25.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_26.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_27.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_28.pickle', r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/data/mc_lesionsham/JPAK_29.pickle']

def load_dataset(pathlist,sessionslice=slice(None)):
    return [load_data.load_pickle(path)[sessionslice] for path in pathlist]
    
def plot_dataset_smooth_trial_times(name,dataset):
    window_len = 30
    window = 'flat'
    fig = plt.figure(name + ' smooth trial times')
    plot_session.alternating_color_map(dataset,['r','b'])
    for i,sessions in enumerate(dataset):
        plot_session.plot_smooth_trial_times(name,sessions,window_len=window_len,window=window)
    plt.legend(('lesion','sham'))
    return fig
    
def plot_dataset_average_trial_times(name,dataset):
    fig = plt.figure(name + ' average trial times')
    plot_session.alternating_color_map(dataset,['r','b'])
    for sessions in dataset:
        plot_session.plot_average_trial_times(name,sessions)
    plt.legend(('lesion','sham'))
    return fig
    
def plot_dataset_average_effective_trial_times(name,dataset):
    fig = plt.figure(name + ' average effective trial times')
    plot_session.alternating_color_map(dataset,['r','b'])
    for sessions in dataset:
        plot_session.plot_average_effective_trial_times(name,sessions)
    plt.legend(('lesion','sham'))
    return fig
    
def plot_dataset_average_tip_speed(name,dataset):
    fig = plt.figure(name + ' average tip speed across sessions')
    plot_session.alternating_color_map(dataset,['r','b'])
    for sessions in dataset:
        plot_session.plot_average_tip_speed(name,sessions)
    plt.legend(('lesion','sham'))
    return fig
    
def plot_dataset_average_tip_height(name,dataset):
    fig = plt.figure(name + ' average tip height across sessions')
    plot_session.alternating_color_map(dataset,['r','b'])
    for sessions in dataset:
        plot_session.plot_average_tip_height(name,sessions)
    plt.legend(('lesion','sham'))
    plt.gca().invert_yaxis()
    return fig