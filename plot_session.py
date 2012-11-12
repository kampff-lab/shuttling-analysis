# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import cv
import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcl
from scipy.stats import norm
import analysis_utilities as utils
import image_processing as imgproc
import process_session
from rasterplot import rasterplot

def time_color_map(data,colormap=plt.cm.jet):
    plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(data))])

def plot_time_var(trials):
    time_color_map(trials)
    for trial in trials:
        plt.plot(trial)
        
def plot_time_distributions(name,sessions):
    plt.figure(name + ' spatial time distribution')
    plt.hist(utils.flatten([utils.flatten(process_session.get_clipped_trajectories(session)) for session in sessions]),100)
    plt.xlabel('horizontal progression (pixels)')
    plt.ylabel('total time (frames)')
        
def plot_end_to_end(data):
    offset = 0
    for epoch in data:
        epochlen = len(epoch)
        indices = range(offset,offset+epochlen)
        offset += epochlen
        plt.plot(indices,epoch,'.')
        
def plot_crossing_times(session,fmt='.'):
    plt.figure(session.name + ' crossing times')
    plt.plot(process_session.get_trial_times(session),fmt)
    
def plot_average_crossing_times(merged):
    plt.figure(merged.name + ' average crossing times')
    trial_miu = []
    trial_err = []
    for session in merged.merged_sessions:
        trial_times = process_session.get_trial_times(session)
        miu = np.mean(trial_times)
        sigma = np.std(trial_times)
        trial_miu.append(miu)
        trial_err.append(sigma)
    plt.bar(range(len(merged.merged_sessions)), trial_miu, yerr = [np.zeros(len(trial_err)),trial_err])
    
def plot_crossing_times_end_to_end(name,sessions):
    plt.figure(name + ' crossing times')
    time_color_map(sessions,plt.cm.jet)
    plot_end_to_end([process_session.get_trial_times(session) for session in sessions])
    plt.xlabel('trials')
    plt.ylabel('crossing time (s)')
        
def plot_progression(session):
    plt.figure(session.name + ' progression')
    time_color_map(session.tip_horizontal)
    for i in range(len(session.tip_horizontal)):
        normalized = np.array(session.tip_horizontal[i])
        invalid_indices = normalized == -1
        if i in session.left_crossings:
            normalized = 1078 + normalized * -1
        normalized[invalid_indices] = np.nan
        plt.plot(normalized)
        
def plot_progression_path(session):
    plt.figure(session.name + ' progression')
    time_color_map(session.tip_horizontal_path)
    for path in session.tip_horizontal_path:
        normalized = np.array(path)
        plt.plot(normalized)
    plt.xlabel('time (frames)')
    plt.ylabel('progression (pixels)')
        
def plot_progression_delta_path(session):
    plt.figure(session.name + ' progression delta')
    time_color_map(session.tip_horizontal_path)
    for path in session.tip_horizontal_path:
        normalized = np.array(path)
        plt.plot(np.diff(normalized))
    plt.xlabel('time (frames)')
    plt.ylabel('progression delta (pixels)')

def plot_tip_spatial_speed_trial(session,i):
    plt.figure(session.name + ' ' + session.session_type + ' speed')
    speed_spline,speed,decision = process_session.get_tip_spatial_speed_trial(session,i)
    if decision:
        plt.plot(speed_spline)
    
def plot_tip_spatial_speed(session):
    plt.figure(session.name + ' ' + session.session_type + ' speed')
    data = []
    for i in range(len(session.tip_horizontal)):
        print i,len(data)
        speed_spline,speed,decision = process_session.get_tip_spatial_speed_trial(session,i)
        if decision:
            data.append(speed_spline)
    im = plt.imshow(data,vmin=0,vmax=10)
    plt.colorbar(im)
    return data

def plot_tip_trajectory(session,i):
    plt.figure(session.name + ' ' + session.session_type + ' trajectory')
    x,y,decision = process_session.get_tip_trajectory_trial(session,i)
    if decision:
        plt.plot(x,y)
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    
def plot_tip_trajectories(session):
    plt.figure(session.name + ' ' + session.session_type + ' trajectory')
    for i in range(len(session.tip_horizontal)):
        x,y,decision = process_session.get_tip_trajectory_trial(session,i)
        if decision:
            plt.plot(x,y)
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
        
def plot_latency_curves(name,sessions):
    plt.figure(name + ' cumulative latency')
    time_color_map(sessions)
    for session in sessions:
        latency = np.cumsum([interval.total_seconds() for interval in session.inter_reward_intervals])
        plt.plot(latency)
        for i in range(len(latency)):
            plt.plot(i,latency[i],'k|')
    plt.xlabel('trials')
    plt.ylabel('latency (s)')
    plt.title('cumulative latency')
    
def plot_step_dynamics(name,sessions,step,selector):
    title = name + ' step %s aligned dynamics' % step
    plt.figure(title)
    step_tip_trials = [process_session.get_step_aligned_data(selector(session),session,step,120,120,False)[0] for session in sessions]
    im = plt.imshow(utils.flatten(step_tip_trials))
    plt.colorbar(im)
    plt.xlabel('time (frames)')
    plt.ylabel('trials')
    plt.title(title)
    
    trial = 0
    for i,session in enumerate(step_tip_trials):
        im.axes.annotate(sessions[i].name + ' ' + sessions[i].session_type, xy=(0,trial), xycoords='data',
                         xytext=(-350,0),textcoords='offset points',
                         arrowprops=dict(arrowstyle="->"))
        trial += len(session)
    
def plot_step_tip_dynamics(name,sessions,step):
    plot_step_dynamics(name + ' horizontal tip',sessions,step,lambda s:s.tip_horizontal)
    
def plot_step_tip_height_dynamics(name,sessions,step):
    plot_step_dynamics(name + ' vertical tip',sessions,step,lambda s:s.tip_vertical)
    
def plot_step_activity_dynamics(name,sessions,step):
    plot_step_dynamics(name + ' step activity',sessions,step,lambda s:s.step_activity[step])
    
def plot_step_tip_progression(name,sessions):
    plt.figure(name + ' average step aligned tip position')
    step_tip_trials = [[utils.meanstd(process_session.get_step_aligned_data(session.tip_horizontal,session,step)[0]) for session in sessions] for step in range(6)]
    [plt.errorbar(range(len(session_data)),[mean for mean,std in session_data],[std for mean,std in session_data]) for session_data in step_tip_trials]
    
def plot_step_tip_trials_end_to_end(name,sessions):
    plt.figure(name + ' step aligned tip position')
    time_color_map(sessions,plt.cm.hsv)
    step_tip_trials = [[process_session.get_step_aligned_data(session.tip_horizontal,session,step)[0] for session in sessions] for step in range(6)]
    [plot_end_to_end(step_aligned_data) for step_aligned_data in step_tip_trials]
    plt.xlabel('trials')
    plt.ylabel('tip position (pixels)')
    
def plot_step_tip_height_trials_end_to_end(name,sessions):
    plt.figure(name + ' step aligned tip height')
    time_color_map(sessions,plt.cm.spectral)
    step_tip_trials = [[process_session.get_step_aligned_data(session.tip_vertical,session,step)[0] for session in sessions] for step in range(6)]
    [plot_end_to_end(step_aligned_data) for step_aligned_data in step_tip_trials]
    plt.xlabel('trials')
    plt.ylabel('tip height (pixels)')
        
def plot_step_tip_distribution(session,stepindex):
    plt.figure("%s step %s tip distribution" % (session.name, stepindex))
    plt.hist(process_session.step_tip_distribution(session,stepindex))
        
def plot_average_intensity(name,mean):
    plt.figure(name + 'mean')
    plot_time_var(mean)
    plt.xlabel('time (frames)')
    plt.ylabel('average intensity')
    plt.title('trial-by-trial pixel average')
    ax = plt.gca()
    ylim = ax.get_ylim()
    ylim = (2,ylim[1])
    ax.set_ylim(ylim)
    
def plot_step_trials(name,steps):
    plt.figure(name + 'steps')
    rasterplot(steps[0],'b.')
    rasterplot(steps[1],'g.')
    rasterplot(steps[2],'r.')
    rasterplot(steps[3],'c.')
    rasterplot(steps[4],'m.')
    rasterplot(steps[5],'y.')
    ax = plt.gca()
    xlim = ax.get_xlim()
    xlim = (xlim[0],700)
    ylim = ax.get_ylim()[::-1]
    ylim = (ylim[0],1)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    plt.xlabel('time (frames)')
    plt.ylabel('trials')
    plt.title('trial-by-trial step sequence')
    
    plt.figure(name + 'first step distributions')
    x = np.linspace(xlim[0],xlim[1])
    steps = [process_session.index_distribution(steps,slice(1)) for steps in steps]
    for distribution in steps:
        dmean = np.mean(distribution)
        dstd = np.std(distribution)
        plt.plot(x,norm.pdf(x,loc=dmean,scale=dstd))
    ax = plt.gca()
    ylim = ax.get_ylim()
    ax.set_ylim(ylim)
    plt.xlabel('time (frames)')
    plt.ylabel('probability')
    
    plt.figure(name + 'first step cumulative distributions')
    for distribution in steps:
        hist,bins=np.histogram(distribution,bins=100)
        cumulative = np.cumsum(hist)
#        width=0.7*(bins[1]-bins[0])
        center=(bins[:-1]+bins[1:])/2
        plt.plot(center,cumulative)
    
def plot_step_probability(session):
    plt.figure(session.name + 'step probability')
    plt.bar(range(len(session.steps)),process_session.step_probabilities(session))

def plot_session(session):
    plot_average_intensity(session.name,session.mean)
    plot_step_trials(session.name,session.steps)
    plot_step_probability(session)

def plot_speed_raster(name,trials,trial_slice=slice(0,140)):
    speed_trials = process_session.get_tip_horizontal_speed_trials(trials,trial_slice)
    plt.figure(name + 'speed raster')
    plt.imshow(speed_trials,vmin=0,vmax=10)
    
def plot_spatial_speed_distribution(trials):
    m = process_session.get_spatial_speed_distribution(trials)
    bins = m[0][1][1:]
    avg_speeds = (m[1][1:])/(m[2][1:])
    plt.bar(bins[0:len(bins)-1],avg_speeds[0:len(avg_speeds)-1],10)
    
def plot_distance_statistics(name,distances,clusters):
    plt.figure(name + ' distance matrix')
    plt.imshow(distances)
    
    plt.figure(name + ' distance distribution')
    plt.hist(utils.flatten(distances),100)
    
    plt.figure(name + ' cluster dendrogram')
    hcl.dendrogram(clusters)
    
def plot_average(name,images):
    mean = imgproc.average_image_list(images)
    cv.NamedWindow(name,cv.CV_WINDOW_NORMAL)
    cv.ShowImage(name,mean)
    del mean
    
def plot_image_tiles(name,tiles,mosaicscale=2):
    if len(tiles) > 0:
        mosaic_size = mosaicscale * np.array(cv.GetSize(tiles[0]))
        mosaic = cv.CreateImage(mosaic_size,tiles[0].depth,tiles[0].channels)
        ntiles = np.ceil(np.sqrt(len(tiles)))
        tile_scale = mosaicscale / ntiles
        tile_size = (int(tiles[0].width * tile_scale),int(tiles[0].height * tile_scale))
        for i in xrange(len(tiles)):
            image = tiles[i]
            xtile = int(i % ntiles)
            ytile = int(i / ntiles)
            roi = (int(xtile * tile_size[0]),int(ytile * tile_size[1]),tile_size[0],tile_size[1])
            cv.SetImageROI(mosaic,roi)
            cv.Resize(image,mosaic)
        cv.ResetImageROI(mosaic)
        cv.NamedWindow(name,cv.CV_WINDOW_NORMAL)
        cv.ShowImage(name,mosaic)
        del mosaic
        
def plot_posture_clusters(session,images,clusters,t):
    fclusters = hcl.fcluster(clusters,t,'maxclust')
    img_clusters = process_session.split_clusters(images,fclusters)
    for i in xrange(len(img_clusters)):
        plot_image_tiles(session.name + ' Cluster%s' % (i), img_clusters[i])
    average_clusters = [imgproc.avgstd_image_list(imgs) for imgs in img_clusters]
    
    plot_image_tiles(session.name + ' Cluster Means and Stds',utils.flatten(zip([avgstd[0] for avgstd in average_clusters],[avgstd[1] for avgstd in average_clusters])))
    
    plt.figure(session.name + 'Cluster Std Comparison')
    plt.bar(range(len(average_clusters)),[cv.Sum(img[0])[0] for img in average_clusters])
    del average_clusters