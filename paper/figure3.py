# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 13:01:25 2014

@author: Gonçalo
"""

import os
import trials
import trajectories
import numpy as np
import scipy.stats as stats
import dateutil.parser as tparser
import matplotlib.pyplot as plt
    
def timedelta(data):
    return np.array([delta.total_seconds()
    for delta in np.diff(np.array([tparser.parse(d) for d in data]))])

def figure3(paths):
    stable = []
    unstable = []
    for path in paths:
        
        traj = trajectories.genfromtxt(path)
        steps = np.genfromtxt(os.path.join(path,'Analysis\step_activity.csv'))
        time = np.genfromtxt(os.path.join(path,'front_video.csv'),dtype=str)
        trajtrials = trials.gettrialindices(path)
        stepstate = trials.gettrialstate(os.path.join(path,'step3_trials.csv'),trajtrials)
        
        ftraj = trajectories.heightfilter(trajectories.lengthfilter(traj,0,500),0,6)
        
    #    plt.figure()
    #    for t in traj.tolist():
    #        plt.plot(len(t),max(t[:,1]),'k.')
    #    for t in ftraj.tolist():
    #        plt.plot(len(t),max(t[:,1]),'r.')
        
        traj = trajectories.mirrorleft(ftraj)
        #activesteptrials = [sum(steps[s,3 if s.step < 0 else 2]) / 255 for s in traj.slices]
        activesteptrials = [s for s in traj.slices
        if (sum(steps[s,3 if s.step < 0 else 2]) / 255) > 500]
        traj = trajectories.trajectories(traj.data,activesteptrials)
    
    #    plt.figure()    
    #    for t in traj.tolist():
    #        plt.plot(t[:,0],t[:,1],'k',alpha=0.1)
        
        speed = [np.insert(np.diff(traj.data[s,0])/timedelta(time[s]),0,0)
        for s in traj.slices]
        validtrials = [traj.slices[i] for i,s in enumerate(speed) if np.mean(s) > 0]
        
        traj = trajectories.trajectories(traj.data,validtrials)
        speed = [s for s in speed if np.mean(s) > 0]
        
    #    plt.figure()
    #    for sp in speed:
    #        plt.plot(sp,'k',alpha=0.1)
            
        # Bin (progrssion - X) Speed Profiles (from position 200 to 1200)
        numBins = 25
        binSize = 50 / numBins
        bins = range(0,50,binSize)
        speedbins = np.zeros((len(traj.slices),numBins))
        for i,t in enumerate(traj.tolist()):
            xs = t[:,0]
            binindices = np.digitize(xs,bins)
            for b in range(numBins):
                speedbin = speed[i][binindices == b]
                speedbins[i,b] = np.mean(speedbin) if speedbin.size > 0 else np.nan
            basespeed = stats.nanmean(speedbins[i,0:numBins/3])
            speedbins[i,:] /= basespeed
        
        stabletrials = [i for i,s in enumerate(validtrials) if stepstate[s.start]]
        unstabletrials = [i for i,s in enumerate(validtrials) if not stepstate[s.start]]
        
        stablespeeds = speedbins[stabletrials,:]
        unstablespeeds = speedbins[unstabletrials,:]
        stable.append(stablespeeds)
        unstable.append(unstablespeeds)
        
    def plotcurve(speeds,color):
        x = np.arange(numBins) * binSize
        mu = np.mean(speeds,axis=0)
        sd = np.std(speeds,axis=0)
        plt.plot(x,mu,color,linewidth=3)
        plt.plot(x,mu-sd,'k--')
        plt.plot(x,mu+sd,'k--')
        plt.fill_between(x,mu-sd,mu+sd,alpha=0.1,color=color)
    
    plt.figure()
    stablespeeds = np.concatenate(stable,0)
    unstablespeeds = np.concatenate(unstable,0)
    plotcurve(stablespeeds,'g')
    plotcurve(unstablespeeds,'r')
    return stablespeeds,unstablespeeds