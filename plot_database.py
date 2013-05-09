# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:53:25 2013

@author: IntelligentSystems
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import process_database as procdb
import plot_session as plotses

def plot_weight_distribution(name,database,sessions):
    fig = plot_weights(name,database)
    weights = procdb.get_events(database,'Weight')
    weights = [procdb.get_closest_event(weights,session.start_time) for session in sessions]
    fig = plot_weights(name,weights,color='r')
    
    deprivation_start_times = [event[0] for event in procdb.get_events(database,'WaterDeprivation') if event[2] == 'Start']
    if len(deprivation_start_times) > 0:
        deprivation_start = deprivation_start_times[len(deprivation_start_times) - 1]
        base_weight = float(procdb.get_closest_event(weights,deprivation_start)[2]) * 0.9
        xlim = plt.gca().get_xlim()
        plt.hlines([base_weight],xlim[0],xlim[1])
    return fig

def plot_weights(name,database,**kwargs):
    fig = plt.figure(name + ' weight distribution')
    weight_events = [event for event in database if event[1] == 'Weight']
    weight_times = [mdates.date2num(event[0]) for event in weight_events]
    weights = [float(event[2]) for event in weight_events]
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.bar(weight_times,weights,**kwargs)
    plt.gcf().autofmt_xdate()
    plt.ylabel('Weight (g)')
    plt.xlabel('Time')
    plt.title('weight distribution over time')
    return fig
    
def plot_servo_assay_deprivation(name,database,sessions):
    def get_snack_timestamp(deprivation_events,sessiontime):
        evt = procdb.get_closest_prior_event(deprivation_events,sessiontime)
        if evt is not None:
            return evt[0]
        else:
            return sessiontime
    
    fig = plt.figure(name + ' deprivation times')
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()
    session_times = [session.start_time for session in sessions]
    reward_counts = [len(session.reward_times) for session in sessions]
    deprivation_events = procdb.get_events(database,'WaterDeprivation')
    deprivation_intervals = [sessiontime - get_snack_timestamp(deprivation_events,sessiontime) for sessiontime in session_times]
    deprivation_hours = [interval.total_seconds() / 3600 for interval in deprivation_intervals]
    
    session_times = mdates.date2num(session_times)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    ax1.plot(session_times,deprivation_hours,linestyle='-',marker='o')    
    ax2.plot(session_times,reward_counts,linestyle='-',marker='o',color='g')

    # Shade session protocols
    plotses.shade_session_protocols(sessions,session_times,ax2,plotzero=False)
    
    plt.gcf().autofmt_xdate()
    ax1.set_ylabel('Deprivation Interval',color='b')
    ax2.set_ylabel('Reward Count',color='g')
    plt.xlabel('Session Time')
    plt.title('deprivation intervals per session')
    return fig