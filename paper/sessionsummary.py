# -*- coding: utf-8 -*-
"""
Created on Sat Sep 06 20:42:53 2014

@author: Gonçalo
"""

import os
import dateutil
import trials
import trajectories
import numpy as np
import matplotlib.pyplot as plt
from collectionselector import CollectionSelector

def summarize(path):
    fig = plt.figure()

    # Frame rate
    ax = fig.add_subplot(331)
    vidtime = np.genfromtxt(os.path.join(path, 'Analysis/videotime.csv'))
    ax.hist(1.0 / np.diff(vidtime),100,normed=True)
    ax.set_title('frame rate')
    ax.set_xlabel('fps')
    
    # Trajectories
    ax = fig.add_subplot(332)
    traj = trajectories.genfromtxt(path)
    traj = trajectories.scale(traj)
    for t in traj.tolist():
        ax.plot(t[:,0],t[:,1],'k',alpha=0.2)
    ax.set_title('trajectories')
    ax.set_xlabel('x (cm)')
    ax.set_ylabel('y (cm)')
    trajax = ax
    
    # Draw trial selection
    selecthandles = []
    trajfilter = []
    conditionfilter = []
    def updateselection():
        if len(trajfilter) > 0:
            ind = trajfilter
            if len(conditionfilter) > 0:
                ind = list(set(ind).intersection(conditionfilter))
        else:
            ind = conditionfilter
        
        selector.ind[:] = ind
        selector.updateselection()
        while len(selecthandles) > 0:
            handle = selecthandles.pop()
            if np.iterable(handle):
                for l in handle:
                    l.remove()
                    del l
            del handle
        
        for s in traj.slices[ind]:
            h1 = trajax.plot(traj.data[s,0],traj.data[s,1],'r',alpha=0.5)
            h2 = activityax.plot(trialsteps_x[ind,:],trialsteps[ind,:],'r.')
            h3 = slipax.plot(trialslips_x[ind,:],trialslips[ind,:],'rx')
            selecthandles.append(h1)
            selecthandles.append(h2)
            selecthandles.append(h3)
            
    def onselect(ind):
        trajfilter[:] = ind
        updateselection()
    
    # Trajectory features
    ax = fig.add_subplot(333)
    maxheight = [np.amax(t[:,1]) for t in traj.tolist()]
    duration = [vidtime[s.stop] - vidtime[s.start] for s in traj.slices]
    pts = ax.scatter(duration,maxheight,s=10,marker='D',
                     facecolors='b',edgecolors='none')
    selector = CollectionSelector(ax,pts,color_other='r',onselection=onselect)
    ax.set_title('trajectory features')
    ax.set_xlabel('duration (s)')
    ax.set_ylabel('max height (cm)')
    
    # Reward rate
    ax = fig.add_subplot(334)
    lr = np.genfromtxt(os.path.join(path, 'left_rewards.csv'), dtype=str)
    rr = np.genfromtxt(os.path.join(path, 'right_rewards.csv'), dtype=str)
    rewards = np.sort(np.concatenate((lr,rr)))
    rewardtimes = [dateutil.parser.parse(t) for t in rewards]
    rewardinterval = np.array([d.total_seconds() for d in np.diff(rewardtimes)])
    ax.plot(rewardinterval)
    ax.set_title('reward rate')
    ax.set_xlabel('trials')
    ax.set_ylabel('inter-reward interval (s)')
    
    # Summary statistics (Top)
    ax = fig.add_subplot(335)
    avgsdvheight = np.array([(np.mean(t[:,1]),np.std(t[:,1])) for t in traj.tolist()])
    ax.boxplot(avgsdvheight)
    ax.set_ylabel('height (cm)')
    
    # Summary statistics (Bottom)
    ax = fig.add_subplot(338)
    speed = trajectories.speed(traj,vidtime)
    avgsdvspeed = np.array([(np.abs(np.mean(t[:,0])),np.std(t[:,0])) for t in speed.tolist()])
    ax.boxplot(avgsdvspeed)
    ax.set_ylabel('speed (cm / s)')
    
    # Step activity
    ax = fig.add_subplot(336)
    stepactivity = np.genfromtxt(os.path.join(path, 'Analysis/step_activity.csv'))
    trialsteps = np.array([np.sum(stepactivity[s,:],axis=0) for s in traj.slices])
    stepnumbers = np.arange(8) + 1
    trialsteps_x = np.tile(stepnumbers,(trialsteps.shape[0],1))
    ax.plot(trialsteps_x,trialsteps,'k.')
    ax.set_xlabel('step')
    ax.set_xlim(0,len(stepnumbers)+1)
    ax.set_xticks(stepnumbers)
    activityax = ax
    
    # Slips
    ax = fig.add_subplot(337)
    slipactivity = np.genfromtxt(os.path.join(path, 'Analysis/slip_activity.csv'))
    trialslips = np.array([np.sum(slipactivity[s,:],axis=0) for s in traj.slices])
    gapnumbers = np.arange(7) + 1
    trialslips_x = np.tile(gapnumbers,(trialslips.shape[0],1))
    ax.plot(trialslips_x,trialslips,'kx')
    ax.set_xlabel('step')
    ax.set_xlim(0,len(gapnumbers)+1)
    ax.set_xticks(gapnumbers)
    slipax = ax
    
    # Trial conditions (WARNING! CONSIDER STEP STATE WRAPAROUND!!)
    ax = fig.add_subplot(339)
    width = 0.39    
    trialindices = trials.gettrialindices(path)
    steptrialpath = os.path.join(path, 'step{0}_trials.csv')
    stepstates = np.array([trials.gettrialstate(str.format(steptrialpath,i), trialindices)
    for i in xrange(1,7)]).T
    steptrialstate = np.array([stepstates[s.start,:] for s in traj.slices])
    fractionstabletrials = np.sum(steptrialstate,axis=0)/float(steptrialstate.shape[0])
    fractionstabletrials = np.insert(fractionstabletrials,[0,stepstates.shape[1]],1)
    unstablebars = ax.bar(stepnumbers,np.ones(stepnumbers.shape),width,color='r')
    stablebars = ax.bar(stepnumbers,fractionstabletrials,width,color='g')
    ax.set_title('manipulations')
    ax.set_xlabel('step')
    ax.set_xlim(0+width/2.,len(stepnumbers)+1+width/2.)
    ax.set_xticks(stepnumbers+width/2.)
    ax.set_xticklabels(stepnumbers)
    conditionax = ax
    
    # Select trial conditions
    def selectstepindices(evt,bars,trialstate):
        try:
            step = next(
            i-1 for i,bar in enumerate(bars)
            if bar.contains(evt)[0])
        except StopIteration:
            return []
                    
        if step >= 0 and step < trialstate.shape[1]:  
            ind = np.nonzero(trialstate[:,step])[0]
        else:
            ind = range(trialstate.shape[0])
        return ind

    notsteptrialstate = np.bitwise_not(steptrialstate)    
    def onbuttonpress(evt):
        if evt.inaxes == conditionax:
            ind = selectstepindices(evt,stablebars,steptrialstate)
            if len(ind) == 0:
                ind = selectstepindices(evt,unstablebars,notsteptrialstate)
            conditionfilter[:] = ind
            updateselection()
    ax.figure.canvas.mpl_connect('button_press_event',onbuttonpress)
    
    plt.tight_layout()
    return traj,vidtime,selector