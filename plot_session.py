# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

#import cv
import bisect
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hcl
from scipy.stats import norm
import analysis_utilities as utils
#import image_processing as imgproc
import process_session
from rasterplot import rasterplot
import matplotlib.gridspec as gridspec

protocol_colors = {
    'stable':'g',
    'centerfree':'r',
    'stabletocenterfree':'orange',
    'centerfreetostable':'orange',
    'randomizedcenterfree_day1':'b',
    'randomizedcenterfree_day2':'b',
    'randomizedcenterfree_day3':'b',
    'randomizedcenterfree_day4':'b',
    'degradationrandomizedcenterfree_day1':'b',
    'degradationrandomizedcenterfree_day2':'b',
    'permutationfreepair_day1':'violet',
    'permutationfreepair_day2':'violet',
    'permutationfreepair_day3':'violet',
    'permutationfreepair_day4':'violet',
    'permutationtofullyreleased':'purple',
    'fullyreleased':'purple'
}

def get_protocol_color(label):
    return protocol_colors.get(label,'g')
    
def shade_session_protocols(sessions,session_xdata,axis=None,plotzero=True):
    if axis is None:
        axis = plt.gca()    
    
    session_labels = [session.session_labels.get('protocol') for session in sessions]
    prev_x = 0
    for i,(label,x) in enumerate(zip(session_labels,session_xdata)):
        if i > 0 or plotzero:
            axis.axvspan(prev_x,x,facecolor=get_protocol_color(label),alpha=0.5,lw=0)
        prev_x = x

def click_data_action(figure,ondataclick):
    def onclick(event):
        if event.button == 3 and event.xdata is not None and event.ydata is not None:
            ondataclick(event)
    figure.canvas.mpl_connect('button_press_event',onclick)
    
def get_color_cycle(data,colormap=plt.cm.jet):
    return [colormap(i) for i in np.linspace(0, 0.9, len(data))]
    
def get_alternating_color_cycle(data,colors):
    return [colors[i % len(colors)] for i in range(len(data))]
    
def alternating_color_map(data,colors):
    plt.gca().set_color_cycle(get_alternating_color_cycle(data,colors))

def time_color_map(data,colormap=plt.cm.jet):
    plt.gca().set_color_cycle(get_color_cycle(data,colormap))

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
        
def plot_end_to_end_xy(data):
    offset = 0
    for x,y,epochlen in data:
        x += offset
        offset += epochlen
        plt.plot(x,y,'.')
        
def bar_end_to_end(data,colorcycle):
    offset = 0
    rects = []
    for i in range(len(data)):
        epoch = data[i]
        epochlen = len(epoch)
        indices = range(offset,offset+epochlen)
        offset += epochlen
        rects.append(plt.bar(indices,epoch,facecolor=colorcycle[i]))
    return rects
        
def plot_crossing_times(session,fmt='.'):
    plt.figure(session.name + ' crossing times')
    plt.plot(process_session.get_first_crossing_trial_times(session),fmt)
    
def plot_average_crossing_times(merged):
    plt.figure(merged.name + ' average crossing times')
    trial_miu = []
    trial_err = []
    for session in merged.merged_sessions:
        trial_times = process_session.get_first_crossing_trial_times(session)
        miu = np.mean(trial_times)
        sigma = np.std(trial_times)
        trial_miu.append(miu)
        trial_err.append(sigma)
    plt.bar(range(len(merged.merged_sessions)), trial_miu, yerr = [np.zeros(len(trial_err)),trial_err])
    
def plot_average_tip_height_all_conditions(name,sessions):
    plot_average_tip_height_light_trials(name,sessions)
    plot_average_tip_height_light_change(name,sessions)
    plot_average_tip_height_direction_trials(name,sessions)
    
def plot_average_tip_height_light_trials(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_height_two_conditions(name,'light','dark',sessions,lambda s:s.light_trials,crop=crop)
    
def plot_average_tip_height_light_change(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_height_two_conditions(name,'change','no change',sessions,lambda s:np.insert(np.diff(s.light_trials),0,1),crop=crop)
    
def plot_average_tip_height_direction_trials(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_height_two_conditions(name,'left','right',sessions,lambda s:np.array(s.crossing_direction),crop=crop)
    
def plot_average_tip_height_two_conditions(name,condition1,condition2,sessions,selector,crop=process_session.default_crop):
    figurename = "%s %s/%s" % (name,condition1,condition2)
    plot_average_tip_height_end_to_end(figurename,sessions,selector,colors='r',crop=crop)
    ax = plt.gca()
    line = ax.lines[0]
    line.set_label(condition1)
    
    fig = plot_average_tip_height_end_to_end(figurename,sessions,lambda s:~selector(s),colors='b',invert_y=False,crop=crop)
    ax = plt.gca()
    line = ax.lines[-1]
    line.set_label(condition2)
    plt.legend()
    plt.xlabel('crossings (single animal)')
    return fig
    
def plot_average_tip_height_end_to_end(name,sessions,conditionselector=lambda x:None,colors=['b','r'],invert_y=True,crop=[0,1280]):
    fig = plt.figure(name + ' average tip height')
    alternating_color_map(sessions,colors)
    average_height = [process_session.get_average_crossing_tip_height(session,conditionselector(session),crop) for session in sessions]
    plot_end_to_end_xy(average_height)
    shade_session_protocols(sessions,np.cumsum([epochlen for x,y,epochlen in average_height]))
    plt.xlabel('crossings (single animal, session colored)')
    plt.ylabel('average tip height (pixels)')
    plt.title('average height of the tip of the nose during successive crossings')
    if invert_y:
        ax = plt.gca()
        ax.invert_yaxis()
    return fig
    
def plot_average_tip_speed_light_trials(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_speed_two_conditions(name,'light','dark',sessions,lambda s:s.light_trials,crop=crop)
    
def plot_average_tip_speed_light_change(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_speed_two_conditions(name,'change','no change',sessions,lambda s:np.insert(np.diff(s.light_trials),0,1),crop=crop)
    
def plot_average_tip_speed_direction_trials(name,sessions,crop=process_session.default_crop):
    return plot_average_tip_speed_two_conditions(name,'left','right',sessions,lambda s:np.array(s.crossing_direction),crop=crop)    
    
def plot_average_tip_speed_two_conditions(name,condition1,condition2,sessions,selector,crop=process_session.default_crop):
    figurename = "%s %s/%s" % (name,condition1,condition2)
    plot_average_tip_speed_end_to_end(figurename,sessions,selector,colors='r',crop=crop)
    ax = plt.gca()
    line = ax.lines[0]
    line.set_label(condition1)
    
    fig = plot_average_tip_speed_end_to_end(figurename,sessions,lambda s:~selector(s),colors='b',crop=crop)
    ax = plt.gca()
    line = ax.lines[-1]
    line.set_label(condition2)
    plt.legend()
    plt.xlabel('crossings (single animal)')
    return fig
        
def plot_average_tip_speed_end_to_end(name,sessions,conditionselector=lambda x:None,colors=['b','r'],crop=process_session.default_crop):
    fig = plt.figure(name + ' average tip speed')
    alternating_color_map(sessions,colors)
    average_speed = [process_session.get_average_crossing_tip_speed(session,conditionselector(session),crop) for session in sessions]
    plot_end_to_end_xy(average_speed)
    shade_session_protocols(sessions,np.cumsum([epochlen for x,y,epochlen in average_speed]))
    plt.xlabel('crossings (single animal, session colored)')
    plt.ylabel('average tip speed (pixels / frame)')
    plt.title('average speed of the tip of the nose during successive crossings')
    return fig
    
def plot_trial_times_end_to_end(name,sessions,conditionselector=lambda x:None):
    fig = plt.figure(name + ' trial times')
    #time_color_map(sessions,plt.cm.jet)
    trial_time_color = get_alternating_color_cycle(sessions,['b'])
    effective_time_color = get_alternating_color_cycle(sessions,['r'])
    effective_trial_times = [process_session.get_first_crossing_trial_times(session,conditionselector(session)) for session in sessions]
    trial_times = [[i.total_seconds() for i in session.inter_reward_intervals] for session in sessions]
    rects_total = bar_end_to_end(trial_times,trial_time_color)
    rects_effective = bar_end_to_end(effective_trial_times,effective_time_color)
    boundaries = process_session.get_boundary_indices(trial_times)
    if len(boundaries) > 0:
        ylim = plt.gca().get_ylim()
        plt.vlines(boundaries,ylim[0],ylim[1])
    
    plt.xlabel('trials (single animal)')
    plt.ylabel('time to reward (s)')
    plt.title('session trial times')
    plt.legend([rects_total[0][0],rects_effective[0][0]],('total time','from first crossing'))
    
    # Interactive video playback feature
    def click_playback(figure,sessions):
        def ondataclick(event):
            x = int(round(event.xdata))
            datasession = None
            time = None
            trial_total = 0
            for i in range(len(sessions)):
                len_session = len(trial_times[i])
                print x,len_session,trial_total
                if x < trial_total + len_session:
                    datasession = sessions[i]
                    x = x - trial_total - 1
                    if x >= 0:
                        time = datasession.reward_times[x]
                    else:
                        time = datasession.start_time
                    break
                trial_total = trial_total + len_session
            
            pos_msec = process_session.get_time_video_pos_msec(datasession,time)
            fps = 120
            video = '\\..\\top_video.avi'
            if event.key == 'f':
                video = '\\..\\front_video.avi'
            imgproc.play_video(datasession.path[0] + video,datasession.name + ' ' + str(pos_msec) + 'msec',pos_msec,fps)
        click_data_action(figure,ondataclick)
    click_playback(fig,sessions)
    return fig
    
def plot_effective_trial_times_end_to_end(name,sessions,conditionselector=lambda x:None,colors=['b','r']):
    fig = plt.figure(name + ' effective trial times')
    alternating_color_map(sessions,colors)
    effective_trial_times = [process_session.get_first_crossing_trial_times(session,conditionselector(session)) for session in sessions]
    plot_end_to_end(effective_trial_times)
    shade_session_protocols(sessions,process_session.get_all_boundary_indices(effective_trial_times))
    plt.xlabel('trials (single animal, session colored)')
    plt.ylabel('time to reward (s)')
    plt.title('interval between start of first crossing and poke head entry')
    return fig
    
def plot_min_trial_times(name,sessions):
    fig = plt.figure(name + ' min trial times')
    sorted_session_trial_times = [np.sort(session.inter_reward_intervals) for session in sessions]
    min_trial_times = [(sorted_trial_times[0].total_seconds() if sorted_trial_times.any() else None) for sorted_trial_times in sorted_session_trial_times]

    valid_times = [min_trial_time if min_trial_time else 0 for min_trial_time in min_trial_times]
    valid_faces = plt.bar(range(len(sessions)),valid_times)
    
    ylim = plt.gca().get_ylim()[1]
    invalid_times = [0 if min_trial_time else ylim for min_trial_time in min_trial_times]
    if np.sum(invalid_times) > 0:
        invalid_faces = plt.bar(range(len(sessions)),invalid_times,color='r')
        plt.legend([valid_faces[0],invalid_faces[0]],('rewarded','no rewards'))
    else:
        plt.legend([valid_faces[0]],['rewarded'])
    
    plt.xlabel('sessions')
    plt.ylabel('time to reward (s)')
    plt.title('minimum trial time across sessions')
    return fig
        
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
    trial_map = {}
    for i in range(len(session.tip_horizontal)):
        print i,len(data)
        speed_spline,speed,decision = process_session.get_tip_spatial_speed_trial(session,i)
        if decision:
            trial_map[len(data)] = i
            data.append(speed_spline)
    im = plt.imshow(data,vmin=0,vmax=10)
    plt.colorbar(im)
    return trial_map
    
def plot_spatial_variable_interpolation_split(fig,session,selector,vmin=None,vmax=None):
    data = []
    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=0.2, hspace=0.2)
    fig.subplots_adjust(**adjustprops)
    for i in range(len(session.tip_horizontal)):
        value = selector(session,i)
        data.append(value)
        
    if session.session_type == 'merge':
        sessions = session.merged_sessions
    else:
        sessions = [session]
        
    root = None
    for i in range(len(sessions)):
        if root is None:
            ax = fig.add_subplot(len(sessions),1,i + 1)
            for label in ax.get_xticklabels():
                label.visible = False
            root = ax
        else:
            ax = fig.add_subplot(len(sessions),1,i + 1, sharex=root, sharey=root)
        
        im = plt.imshow(data,vmin=vmin,vmax=vmax)
        plt.colorbar(im)

    [plt.axvline(step-100,linewidth=2,color='r') for step in process_session.roi_step_centers]        
    plt.xlabel('horizontal position (pixels)')
    plt.ylabel('trials')
    #plt.xticks(np.array(process_session.roi_step_centers)-100)
    
def plot_spatial_variable_interpolation(fig,session,selector,vmin=None,vmax=None):
    data = []
    for i in range(len(session.tip_horizontal)):
        value = selector(session,i)
        data.append(value)
        
    im = plt.imshow(data,vmin=vmin,vmax=vmax)
    cb = plt.colorbar(im)
    [plt.axvline(step-process_session.interpolation_range[0],linewidth=2,color='k') for step in process_session.roi_step_centers]
    if session.session_type == 'merge':
        for i,boundary in enumerate(np.insert(np.cumsum([len(s.trial_time) for s in session.merged_sessions][:-1]),0,0)):
            if i == 0:
                continue
            color = 'k'
            if session.merged_sessions[i].session_type == 'manipulation':
                color = 'r'
            #plt.axhline(boundary,linewidth=5,color='b')
            #annotation = session.merged_sessions[i].name + ' ' + session.merged_sessions[i].session_type
            im.axes.annotate('', xy=(0,boundary), xycoords='data',
                         xytext=(-50,0),textcoords='offset points',
                         arrowprops=dict(facecolor=color,arrowstyle='wedge'))
            
            #im.axes.annotate(annotation, xy=(0,boundary), xycoords='data',
            #             xytext=(-130,-4),textcoords='offset points')
        
        #[plt.axhline(boundary,linewidth=2,color='b') for boundary in np.cumsum([len(s.trial_time) for s in session.merged_sessions][:-1])]

    #im.axes.set_yticklabels(labels)
    #im.axes.get_yaxis().set_ticks([])
    plt.xlabel('horizontal position (pixels)')
    plt.ylabel('crossings')
    plt.xticks(np.array(process_session.roi_step_centers)-process_session.interpolation_range[0],np.array(process_session.roi_step_centers))
    
    # Interactive video playback feature
    def click_playback(figure,session,selector = lambda y:y):
        def ondataclick(event):
            y = int(round(event.ydata))
            datasession = session
            if session.session_type == 'merge':
                trial_total = 0
                for i in range(len(session.merged_sessions)):
                    len_session = len(session.merged_sessions[i].trial_time)
                    if y < trial_total + len_session:
                        datasession = session.merged_sessions[i]
                        y = y - trial_total
                        break
                    trial_total = trial_total + len_session
            
            y = selector(y)
            pos_msec = process_session.get_trial_video_pos_msec(datasession,y)
            imgproc.play_video(datasession.path[0] + '\\..\\front_video.avi',datasession.name,pos_msec,0)
        click_data_action(figure,ondataclick)
    click_playback(fig,session)
    return cb
    
def plot_tip_spatial_height_interp(session,vmin=600,vmax=700):
    fig = plt.figure(session.name + ' position tip height ')
    cb = plot_spatial_variable_interpolation(fig,session,(lambda s,i:process_session.get_spatial_tip_height_trial(s,i)),vmin,vmax)
    plt.title('distribution of nose tip height with position')
    if cb is not None:
        cb.set_label('tip height (pixels)')
        cb.ax.invert_yaxis()
    return fig
    
def plot_tip_spatial_speed_interp(session,vmin=0,vmax=20):
    fig = plt.figure(session.name + ' position tip speed')
    cb = plot_spatial_variable_interpolation(fig,session,(lambda s,i:process_session.get_tip_horizontal_speed_trial(s,i)),vmin,vmax)
    plt.title('distribution of nose tip speed with position')
    cb.set_label('tip speed (pixels / frame)')
    return fig

def plot_tip_trajectory(session,i):
    plt.figure(session.name + ' ' + session.session_type + ' trajectory')
    x,y,decision = process_session.get_tip_trajectory_trial(session,i)
    if decision:
        plt.plot(x,y)
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    
def plot_tip_trajectories(session,crop=[0,1280]):
    lplot = None
    rplot = None
    fig = plt.figure(session.name + ' ' + session.session_type + ' trajectory')
    for i in range(1,len(session.tip_horizontal)-1):
        x,y,rdir = process_session.get_tip_trajectory_trial(session,i,crop)
        #plt.plot(x,y)
        if rdir:
            rplot, = plt.plot(x,y,'b')
        else:
            lplot, = plt.plot(x,y,'r')
   
    #[plt.axvline(center,linewidth=2,color='k') for center in np.array(process_session.roi_step_centers)]
    #plt.xlabel('horizontal position (pixels)')
    #plt.ylabel('vertical position (pixels)')
    #plt.title('tracked nose tip trajectories')
    #plt.xticks(np.array(process_session.roi_step_centers))
    plt.legend([lplot,rplot],('left','right'),loc=4)
                
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    return fig
        
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
    step_tip_trials = [process_session.get_step_aligned_data(selector(session),session,step,120,120,False)[1] for session in sessions]
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
    
def plot_step_tip_height_trials_end_to_end(name,sessions,step):
    plt.figure(name + ' step aligned tip height')
    time_color_map(sessions,plt.cm.spectral)
    step_tip_trials = [process_session.get_step_aligned_data(session.tip_horizontal,session,step)[0] for session in sessions]
    #step_tip_trials = [utils.nanmean(process_session.get_step_aligned_data(session.tip_horizontal,session,step)[0]) for session in sessions]
    plot_end_to_end(step_tip_trials)
    #plt.plot(step_tip_trials)
    plt.xlabel('trials')
    plt.ylabel('tip height (pixels)')
    
def plot_step_tip_position(name,sessions,steps):
    plt.figure(name + ' step aligned tip position')
    gs = gridspec.GridSpec(2,2,width_ratios=[8,1],height_ratios=[1,8],wspace = 0.05,hspace = 0.05)
    #time_color_map(sessions,plt.cm.spectral)
    plt.subplot(gs[2])
    alternating_color_map(sessions,['black','orange'])
    step_tip_trials_x = [[process_session.get_step_aligned_data(session.tip_horizontal,session,step)[0] for session in sessions] for step in steps]
    step_tip_trials_y = [[process_session.get_step_aligned_data(session.tip_vertical,session,step)[0] for session in sessions] for step in steps]
    
    step_tip_trial_sessions_x = []
    step_tip_trial_sessions_y = []
    for i in range(len(step_tip_trials_x)):
        for s in range(len(step_tip_trials_x[i])):
            for k in range(len(step_tip_trials_x[i][s])):
                if s >= len(step_tip_trial_sessions_x):
                    step_tip_trial_sessions_x.append([])
                    step_tip_trial_sessions_y.append([])
                step_tip_trial_sessions_x[s].append(step_tip_trials_x[i][s][k])
                step_tip_trial_sessions_y[s].append(step_tip_trials_y[i][s][k])
    
    [plt.plot(step_tip_trial_sessions_x[i],step_tip_trial_sessions_y[i],'.') for i in range(len(step_tip_trial_sessions_x))]
    plt.xlabel('horizontal position (pixels)')
    plt.ylabel('vertical position (pixels)')
    plt.title('nose tip positions aligned on step events (single animal)')
    plt.xticks(np.array(process_session.roi_step_centers))
    plt.legend([session.session_type for session in sessions])
    ax = plt.gca()
    ax.set_ylim(ax.get_ylim()[::-1])
    
    plt.subplot(gs[0])
    alternating_color_map(sessions,['black','orange'])
    
    step_tip_trial_sessions_x = [utils.removenan(session) for session in step_tip_trial_sessions_x]
    step_tip_trial_sessions_y = [utils.removenan(session) for session in step_tip_trial_sessions_y]
    minx = np.min([np.min(session) for session in step_tip_trial_sessions_x])
    maxx = 1075.0
    miny = np.min([np.min(session) for session in step_tip_trial_sessions_y])
    maxy = np.max([np.max(session) for session in step_tip_trial_sessions_y])
    
    bins = np.linspace(minx, maxx, 100)
    [plt.hist(step_tip_trial_sessions_x[i],100,range=(minx,maxx),alpha=1-(i*0.5),histtype='stepfilled') for i in range(len(step_tip_trial_sessions_x))]
    plt.xticks([])
    plt.yticks([])
    plt.subplot(gs[3])
    alternating_color_map(sessions,['black','orange'])
    bins = np.linspace(miny, maxy, 100)
    [plt.hist(step_tip_trial_sessions_y[i],bins,alpha=1-(i*0.5),orientation='horizontal',histtype='stepfilled') for i in range(len(step_tip_trial_sessions_y))]
    ax = plt.gca()
    plt.xticks([])
    plt.yticks([])
    ax.set_ylim(ax.get_ylim()[::-1])
    #plt.xlim(0,14)
    plt.xlim(0,40)
    #return step_tip_trial_sessions_x
    
def plot_step_average_variable(name,sessions,selector):
    plt.figure(name + ' step aligned tip height')
    time_color_map(sessions,plt.cm.spectral)
    
    step_tip_trials = [[process_session.get_step_aligned_data(selector(session),session,step)[0] for session in sessions] for step in range(6)]    
    step_tip_trials = [[np.ma.masked_array(session,np.isnan(session)) for session in step] for step in step_tip_trials]

    plt.boxplot(step_tip_trials[2])
    #plt.bar(range(8),step_tip_trials[2])
#    [plot_end_to_end(step_aligned_data) for step_aligned_data in step_tip_trials]
    plt.xlabel('trials')
    plt.ylabel('tip height (pixels)')
    
def plot_step_average_tip_height(name,sessions):
    plt.figure(name + ' step aligned tip height')
    time_color_map(sessions,plt.cm.spectral)
    
    step_tip_trials = [[process_session.get_step_aligned_data(session.tip_vertical,session,step)[0] for session in sessions] for step in range(6)]    
    step_tip_trials = [[np.ma.masked_array(session,np.isnan(session)) for session in step] for step in step_tip_trials]

    plt.boxplot(step_tip_trials[2])
    #plt.bar(range(8),step_tip_trials[2])
#    [plot_end_to_end(step_aligned_data) for step_aligned_data in step_tip_trials]
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
    
def plot_step_activity(session,step):
    plt.figure(session.name + ' step %s activity' % (step))
    [plt.plot(activity) for activity in session.step_activity[step]]
    plt.xlabel('time (frames)')
    plt.ylabel('roi activity (pixels)')
    plt.title('step activity')
    
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
    
#def plot_step_probability(session):
#    plt.figure(session.name + 'step probability')
#    plt.bar(range(len(session.steps)),process_session.step_probabilities(session))
    
def plot_step_probability(name,sessions,colorcycle=None):
    width = 0.9 / (len(sessions) + 1)
    ind = np.arange(6)
    fig = plt.figure(name + ' skip probability')
    ax = fig.add_subplot(111)
    if colorcycle is None:
        colorcycle = get_color_cycle(sessions,plt.cm.spectral)
        
    barplots = []
    for i in range(len(sessions)):
        barplots.append(plt.bar(ind + i * width, process_session.step_probabilities(sessions[i]), width, color = colorcycle[i]))
        
    ax.set_xticks(ind + 0.5 * width * len(sessions))
    ax.set_xticklabels( ('1', '2', '3', '4', '5', '6') )
    
    display = (0,4)
    ax.legend([barplots[i] for i in display],('stable','manipulation'),bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
       ncol=2, mode="expand", borderaxespad=0.)
    
    #ax.legend(('black','red'))
    #ax.legend(barplots,[session.name for session in sessions],bbox_to_anchor=(0, 0, 1, 1), bbox_transform=fig.transFigure)
    #plt.xlabel('step skipped\n(single animal across all sessions)')
    #plt.ylabel('probability of skipping a step')
    #plt.title('probability of skipping each step')

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
    
def plot_session_activity(session):
    legend_plots = []
    legend_labels = []
    
    fig = plt.figure(session.name + ' session activity')
    ax1 = fig.add_subplot('111')
    legend_plots.append(ax1.plot_date(mdates.datestr2num(session.left_poke[1]),session.left_poke[0] - np.min(session.left_poke[0]),'y')[0])
    legend_labels.append('Left Poke')
    
    legend_plots.append(ax1.plot_date(mdates.datestr2num(session.right_poke[1]),session.right_poke[0] - np.min(session.right_poke[0]),'k')[0])
    legend_labels.append('Right Poke')
    plt.xlabel('Time')
    plt.ylabel('Poke Activation (a.u.)')
    
    if session.front_activity is not None:
        ax2 = ax1.twinx()
        activity_time = mdates.datestr2num([session.frame_time[i] for i in range(len(session.front_activity))])
        legend_plots.append(ax2.plot_date(activity_time,session.front_activity, 'g')[0])
        legend_labels.append('Front Activity')
        plt.ylabel('Front motion (pixels/frame)')

    ylim = ax1.get_ylim()    
    if len(session.left_rewards) > 0:
        left_rewards = mdates.datestr2num([session.left_poke[1][bisect.bisect_left(session.left_poke[1],reward)] for reward in session.left_rewards])
        legend_plots.append(ax1.vlines(left_rewards,ylim[0],ylim[1],'r'))
        legend_labels.append('Rewards')

    if len(session.right_rewards) > 0:
        right_rewards = mdates.datestr2num([session.right_poke[1][bisect.bisect_left(session.right_poke[1],reward)] for reward in session.right_rewards])
        ax1.vlines(right_rewards,ylim[0],ylim[1],'r')
    
    ax2.legend(tuple(legend_plots),tuple(legend_labels))
    plt.title('left/right poke activation')
    return fig
    
def plot_poke_statistics(name,sessions):
    barwidth = 0.35
    fig = plt.figure(name + ' poke activation')
    left_pokes = map(list, zip(*[utils.meanstd(session.left_poke[0][session.left_poke[0] > 200]) for session in sessions]))
    right_pokes = map(list, zip(*[utils.meanstd(session.right_poke[0][session.right_poke[0] > 200]) for session in sessions]))
    
    ax = fig.add_subplot(111)
    indices = np.arange(len(sessions))
    left_rects = ax.bar(indices, left_pokes[0], barwidth, color='r', yerr=left_pokes[1])
    right_rects = ax.bar(indices+barwidth, right_pokes[0], barwidth, color='y', yerr=right_pokes[1])

    ax.set_xlabel('Sessions')
    ax.set_ylabel('Activation (a.u.)')
    ax.set_title('Reward-triggered poke activation values')
    ax.set_xticks(indices+barwidth)
    ax.set_xticklabels( [session.name for session in sessions] )
    ax.legend( (left_rects[0], right_rects[0]), ('Left Poke', 'Right Poke') )
    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                    ha='center', va='bottom')
                
    autolabel(left_rects)
    autolabel(right_rects)    
    return fig
    
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