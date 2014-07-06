# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:26:47 2012

@author: IntelligentSystems
"""

import numpy as np
import analysis_utilities as utils
import process_trajectories as proctraj
import process_stepactivity as procsteps
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
import video_player as player
import scipy.stats as scistats

def get_color_cycle(data,colormap=plt.cm.jet):
    return [colormap(i) for i in np.linspace(0, 0.9, len(data))]

def plot_pca2(name,basis,groups,legend=False):
    fig = plt.figure(name)
    ax = fig.add_subplot(111)
    projections = [basis.project(g) for g in groups]
    [plt.plot(p[:,0],p[:,1],'o',label='group%s' % i,alpha=0.5) for i,p in enumerate(projections)]
    if legend:
        ax.legend()
    return projections

def plot_pca3(name,basis,groups,legend=False):
    fig = plt.figure(name)
    ax = fig.add_subplot(111,projection='3d')
    projections = [basis.project(g) for g in groups]
    [plt.plot(p[:,0],p[:,1],p[:,2],'.',label='group%s' % i) for i,p in enumerate(projections)]
    if legend:
        ax.legend()
    return projections
    
def pca_basis(dataset):
    return mpl.mlab.PCA(np.concatenate(dataset))

def plot_trajectories(trajectories,slices):
    fig = plt.figure()
    [plt.plot(trajectories[s,0],trajectories[s,1],picker=5,zorder=i) for i,s in enumerate(slices)]
    plt.gca().invert_yaxis()
    return fig
    
step_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

def contains_label_filter(labels):
    return lambda i,tlabels:utils.is_dict_subset(labels,tlabels[i])
    
def plot_trajectories_stacked(name,trajectories,slices,video=None,steps=None,labels=None,labelfilter=None):
    fig = plt.figure(name + ' trajectories')
    cmap = plt.cm.autumn
    norm = plt.cm.colors.Normalize(vmin=0,vmax=10)
    lims = [np.inf,-np.inf,np.inf,-np.inf]
    first= [True]
    def plot_trajectory(i,s):
        if callable(labelfilter) and not labelfilter(i,labels):
            return
        x = trajectories[s,0]
        y = trajectories[s,1] + i * 100
        speed = np.insert(proctraj.get_trajectory_speed(trajectories[s,0:2]),0,0)
        
        ###### Plotting manipulation line #####################################
        #if labels[i]['state'] == 'unstable' and first[0]:
        #    first[0]=False
        #    plt.hlines(500 + i * 100 - 50,0,1300,colors='g',lw=4,zorder=1000)
        
#        points = np.array([x,y]).T.reshape(-1,1,2)
#        segments = np.concatenate([points[:-1], points[1:]], axis=1)
#        lc = mpl.collections.LineCollection(segments,cmap=cmap,norm=norm)
#        lc.set_array(speed)
#        plt.gca().add_collection(lc)
        
        plt.scatter(x,y,
                    c=speed,
                    cmap=cmap,
                    norm=norm,
                    marker='o',
                    edgecolors='None',
                    s=5,picker=5,
                    zorder=i)
        if steps is not None:
            steponsets = procsteps.get_step_onsets(steps[i])
            stepx = x[steponsets[0]]
            stepy = y[steponsets[0]]
            for i in range(len(stepx)):
                plt.plot(stepx[i],
                         stepy[i],
                         'o',
                         c=step_colors[steponsets[1][i]],
                         markersize=4,
                         zorder=len(slices))
        lims[0]=min(lims[0],np.min(x))
        lims[2]=min(lims[2],np.min(y))
        lims[1]=max(lims[1],np.max(x))
        lims[3]=max(lims[3],np.max(y))
    
    [plot_trajectory(i,s) for i,s in enumerate(slices)]
    plt.xlim(lims[0],lims[1])
    plt.ylim(lims[2],lims[3])
    plt.gca().invert_yaxis()
    if video is not None:
        plot_trajectories_player(fig,video,trajectories,slices,30)
    return fig
    
def plot_trajectories_player(fig,path,trajectories,slices,playbackrate=0):
    ax = fig.gca()
    def on_pick(event):
        if event.mouseevent.inaxes == ax:
            print event.artist.zorder
            pickslice = slices[event.artist.zorder]
            player.play_video(path,playbackrate,pickslice.start,pickslice.stop)
    return fig.canvas.mpl_connect('pick_event',on_pick)
    
def plot_trajectory_groups(name,trajectories,subjects=None,sessions=None,trials=slice(None),labelfilter=None,drawsteps=True,drawcolorbar=True):
    ax = None
    fig = plt.figure(name + ' trajectories')
    for i,x in enumerate(proctraj.iterate_trajectories(trajectories,subjects,sessions,trials)):
        ax = fig.add_subplot(1,len(subjects) * len(sessions),i + 1)
        plot_trajectories_stacked(name,x[0],x[1],x[2],x[3] if drawsteps else None,x[4],labelfilter)
        ax.set_xticks([425, 850])
        plt.setp(ax.get_yticklabels(),visible=False)
        plt.title('JPAK 2%s' % subjects[i])
        plt.xlabel('X (pixels)')
        if i == 0:
            plt.ylabel('Y (pixels)')
    
    if drawcolorbar:
        fig.subplots_adjust(left=0.05, right=0.9)
        cax = fig.add_axes([0.92, 0.15, 0.025, 0.7])
        #fig.subplots_adjust(left=0.05, right=0.8)
        #cax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        plt.colorbar(None, cax)
        cax.set_ylabel('speed (pixels / frame)')
    plt.suptitle('stacked nose tip trajectories')
    return fig
        
def plot_timeseries(series,**kwargs):
    [plt.plot(s,**kwargs) for s in series]
    
def plot_step_aligned_speed_groups(trajectories,stepindex,subjects=None,sessions=None,trials=slice(None),labelfilter={}):
    fig = plt.figure()
    colors = ['b','g']
    [plt.plot(np.average(proctraj.get_step_aligned_speeds(x[0],x[1],x[3],x[4],stepindex,labelfilter),axis=0),c=colors[i % len(colors)]) for i,x in enumerate(proctraj.iterate_trajectories(trajectories,subjects,sessions,trials))]
    ylims = plt.gca().get_ylim()
    plt.vlines([proctraj._dabefore],ylims[0]+1,ylims[1]-1)
    return fig
    
def plot_step_aligned_horizontal_tip_groups(trajectories,stepindex,subjects=None,sessions=None,trials=slice(None),labelfilter={}):
    fig = plt.figure()
    colors = ['b','g']
    [plot_timeseries(proctraj.get_step_aligned_horizontal_tips(x[0],x[1],x[3],x[4],stepindex,labelfilter),c=colors[i % len(colors)]) for i,x in enumerate(proctraj.iterate_trajectories(trajectories,subjects,sessions,trials))]
    ylims = plt.gca().get_ylim()
    plt.vlines([proctraj._dabefore],ylims[0]+1,ylims[1]-1)
    return fig
    
def plot_regression_line(xi,yi,**kwargs):
    w0,w1,r,p,err = scistats.linregress(xi,yi)
    line = w0*xi + w1
    kwargs['marker'] = None
    r_string = r'$r_s=%.2f,$' % r**2
    p_string = r'$p < 0.01$' if p < 0.01 else r'$p = %.2f$' % p
    plt.text(max(xi), max(line), r_string+'\n'+p_string,verticalalignment='center')
    return plt.plot(xi,line,**kwargs)

def plot_trajectory_speed_features(name,trajectories,slices,speeds,normalizer=1,**kwargs):
    features = proctraj.preprocess_speed_features(trajectories,slices,speeds,normalizer)
    return plot_speed_features(name,features,**kwargs)
    
def plot_speed_features(name,features,regress=False,**kwargs):
    fig = plt.figure(name + ' speed features')
    regression = None
    if regress:
        regression = plot_regression_line(features[:,1],features[:,0],**kwargs)
    scatter = plt.scatter(features[:,1],features[:,0],picker=True,**kwargs)
    plt.xlabel('avg. speed outside (pixels / frame)')
    plt.ylabel('avg. speed in center (pixels / frame)')
    plt.title('speed at the edges vs. speed in center')
    return (fig,scatter,regression)