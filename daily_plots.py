# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 23:46:23 2013

@author: IntelligentSystems
"""

import os
import glob
import load_data
import plot_session as plts
import process_session as procs
import matplotlib.pyplot as plt
import analysis_utilities as utils
import process_database as procdb
import plot_database as plotdb
import cPickle as pickle

storage_base = r'C:/Users/IntelligentSystems/Documents/Insync/kampff.lab@gmail.com/'
pickled_sessions_storage = storage_base + r'protocols/shuttling/data/mc_lesionsham'
daily_figures_storage = storage_base + r'protocols/shuttling/figures'
comparison_figures_storage = storage_base + r'protocols/shuttling/figures/comparison'
subject_database_storage = storage_base + r'animals'

def get_figurefilename(label,basepath='.'):
    return os.path.join(basepath,label.replace(' ','_').replace('/','_'))

def save_figure(fig,basepath='.'):
    utils.mkdir_p(basepath)
    filename = get_figurefilename(fig.get_label(),basepath)
    fig.savefig(filename + '.png')

def session_summary_servoassay(datafolders,
                               plotdaily=True,
                               updatedaily=False,
                               foldercategories=False,
                               usepickle=False,
                               datapickle=False,
                               sessionslice=slice(None),
                               storagefolder=None):
    currdir = os.getcwd()
    
    valid_positions = [200,1000]
    tip_height_limits = [600,300]
    speed_limits = [0,40]
    for path in datafolders:
        pathsplit = os.path.split(path)
        name = pathsplit[1]
        pathsplit = os.path.split(pathsplit[0])
        protocol = os.path.split(pathsplit[0])[1]
        if storagefolder is None:
            figurefolder = os.path.join(daily_figures_storage,protocol,name)
        else:
            figurefolder = storagefolder
        utils.mkdir_p(figurefolder)
        os.chdir(figurefolder)
        basepath = '.'
        
        # Load data
        pickled_filename = os.path.join(pickled_sessions_storage,name + '.pickle')
        if usepickle:
            with open(pickled_filename,'rb') as pickle_file:
                sessions = pickle.load(pickle_file)
        else:
            sessions = load_data.load_path(path)
        sessions = sessions[sessionslice]
        
        # Save pickled session
        if datapickle:
            with open(pickled_filename,'wb') as pickled_file:
                pickle.dump(sessions,pickled_file,pickle.HIGHEST_PROTOCOL)
        
        # Load database
        database_file = os.path.join(subject_database_storage,name + '.csv')
        database = procdb.load_database(database_file)
        
        # Plot weight distribution over time
        if foldercategories:
            basepath = 'weight'
        fig = plotdb.plot_weight_distribution(name,database,sessions)
        save_figure(fig,basepath)
        
        # Plot deprivation times and reward amount
        if foldercategories:
            basepath = 'deprivation'
        fig = plotdb.plot_servo_assay_deprivation(name,database,sessions)
        save_figure(fig,basepath)
        
        # Plot trial times
        if foldercategories:
            basepath = 'trial_times'
        fig = plts.plot_trial_times_end_to_end(name,sessions)
        save_figure(fig,basepath)
        
        # Plot effective trial times
        if foldercategories:
            basepath = 'effective_trial_times'
        fig = plts.plot_effective_trial_times_end_to_end(name,sessions)
        plt.ylim([0,10])
        save_figure(fig,basepath)
        
        # Plot min trial times
        if foldercategories:
            basepath = 'min_trial_times'
        fig = plts.plot_min_trial_times(name,sessions)
        save_figure(fig,basepath)

        # Plot average tip speed under different conditions
        if foldercategories:
            basepath = 'speed'
        fig = plts.plot_average_tip_speed_end_to_end(name,sessions,crop=valid_positions)
        plt.ylim(speed_limits)
        save_figure(fig,basepath)
        
        # Plot left-right speed
        #fig = plts.plot_average_tip_speed_direction_trials(name,sessions,crop=valid_positions)
        #plt.ylim(speed_limits)
        #save_figure(fig)
        
        # Plot average tip height under different conditions
        if foldercategories:
            basepath = 'height'
        fig = plts.plot_average_tip_height_end_to_end(name,sessions,crop=valid_positions)
        plt.ylim(tip_height_limits)
        save_figure(fig,basepath)
        
        # Plot left-right height
        #fig = plts.plot_average_tip_height_direction_trials(name,sessions,crop=valid_positions)
        #plt.ylim(tip_height_limits)
        #save_figure(fig)
        
        # Plot nose tip height across sessions
        if foldercategories:
            basepath = 'position_height'
        merged_sessions = procs.merge_sessions(name,sessions)
        fig = plts.plot_tip_spatial_height_interp(merged_sessions,vmin=480,vmax=550)
        plt.xlim(valid_positions)
        save_figure(fig,basepath)
        
        # Plot nose tip speed across sessions
        if foldercategories:
            basepath = 'position_speed'
        fig = plts.plot_tip_spatial_speed_interp(merged_sessions,vmin=0,vmax=20)
        plt.xlim(valid_positions)
        save_figure(fig,basepath)

        # Individual session plots
        if plotdaily:
            activityfolder = 'activity'
            trajectoriesfolder = 'trajectories'
            for session in sessions:
                if True:
                    # Plot nose tip trajectories
                    fig = plts.plot_tip_trajectories(session,crop=valid_positions)
                    plt.xlim([0,1280])
                    plt.ylim([680,0])
                    save_figure(fig,trajectoriesfolder)
                    
                if len(glob.glob(get_figurefilename(session.name,activityfolder) + "*")) == 0 or updatedaily:
                    # Plot poke activation        
                    fig = plts.plot_session_activity(session)
                    save_figure(fig,activityfolder)
        del sessions
        plt.close('all')
        
    os.chdir(currdir)