# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 23:46:23 2013

@author: IntelligentSystems
"""

import os
import load_data
import plot_session as plts
import process_session as procs
import matplotlib.pyplot as plt
import analysis_utilities as utils
import process_database as procdb
import plot_database as plotdb

storage_base = r'C:/Users/IntelligentSystems/Documents/Insync/kampff.lab@gmail.com/'
daily_figures_storage = storage_base + r'protocols/shuttling/figures'
subject_database_storage = storage_base + r'animals'

def save_figure(fig):
    filename = fig.get_label().replace(' ','_').replace('/','_')
    fig.savefig(filename + '.png')

def session_summary_servoassay(datafolders):
    currdir = os.getcwd()
    
    valid_positions = [200,1000]
    tip_height_limits = [600,300]
    speed_limits = [0,40]
    for path in datafolders:
        pathsplit = os.path.split(path)
        name = pathsplit[1]
        pathsplit = os.path.split(pathsplit[0])
        protocol = os.path.split(pathsplit[0])[1]
        figurefolder = os.path.join(daily_figures_storage,protocol,name)
        utils.mkdir_p(figurefolder)
        os.chdir(figurefolder)
        
        # Load data
        sessions = load_data.load_path(path)
        
        # Load database
        database_file = os.path.join(subject_database_storage,name + '.csv')
        database = procdb.load_database(database_file)
        
        # Plot weight distribution over time
        fig = plotdb.plot_weight_distribution(name,database,sessions)
        save_figure(fig)
        
        # Plot trial times
        fig = plts.plot_trial_times_end_to_end(name,sessions)
        save_figure(fig)
        
        # Plot effective trial times
        fig = plts.plot_effective_trial_times_end_to_end(name,sessions)
        plt.ylim([0,10])
        save_figure(fig)

        # Plot average tip speed under different conditions
        fig = plts.plot_average_tip_speed_end_to_end(name,sessions,crop=valid_positions)
        plt.ylim(speed_limits)
        save_figure(fig)
        
        fig = plts.plot_average_tip_speed_direction_trials(name,sessions,crop=valid_positions)
        plt.ylim(speed_limits)
        save_figure(fig)
        
        # Plot average tip height under different conditions
        fig = plts.plot_average_tip_height_end_to_end(name,sessions,crop=valid_positions)
        plt.ylim(tip_height_limits)
        save_figure(fig)
        
        fig = plts.plot_average_tip_height_direction_trials(name,sessions,crop=valid_positions)
        plt.ylim(tip_height_limits)
        save_figure(fig)
        
        # Plot nose tip height across sessions
        merged_sessions = procs.merge_sessions(name,sessions)
        fig = plts.plot_tip_spatial_height_interp(merged_sessions,vmin=480,vmax=550)
        plt.xlim(valid_positions)
        save_figure(fig)
        
        # Plot nose tip speed across sessions
        fig = plts.plot_tip_spatial_speed_interp(merged_sessions,vmin=0,vmax=20)
        plt.xlim(valid_positions)
        save_figure(fig)

        # Individual session plots        
        for session in sessions:
            # Plot nose tip trajectories
            fig = plts.plot_tip_trajectories(session,crop=valid_positions)
            plt.xlim([0,1280])
            plt.ylim([680,0])
            save_figure(fig)
            
            # Plot poke activation        
            fig = plts.plot_poke_activation(session)
            save_figure(fig)
        del sessions
        plt.close('all')
        
    os.chdir(currdir)