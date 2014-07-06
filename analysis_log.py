# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 23:29:42 2013

@author: gonca_000
"""

import tilefigure as tlf
import matplotlib.pyplot as plt
import analysis_utilities as utils
import plot_trajectories as plttraj
import process_trajectories as proctraj
import process_stepactivity as procsteps

plt.close('all')
#t = load_pickle(r'C:/Users/gonca_000/Desktop/trajectories.pickle')

# Plot horizontal tip progression aligned on:
#  - step 2 for right-stable trials comparing last sessions of 1st and 3rd week
proctraj._dabefore = 50
proctraj._daafter = 150
figs = [plttraj.plot_step_aligned_horizontal_tip_groups(t,2,
                                               [i],[4,16],slice(None),
                                               {'direction':'right','state':'stable'})
                                               for i in range(10)]
tlf.tilefigures(figs,[5,2])

# Plot horizontal tip progression aligned on:
#  - step 3 for right-stable trials comparing last sessions of 1st and 3rd week
proctraj._dabefore = 150
proctraj._daafter =  150
figs = [plttraj.plot_step_aligned_horizontal_tip_groups(t,3,
                                               [i],[4,16],slice(None),
                                               {'direction':'right','state':'stable'})
                                               for i in range(10)]
tlf.tilefigures(figs,[5,2])

# Plot speed-colored trajectories for:
#  - all animals session 5
figs = plttraj.plot_trajectory_groups(t,None,[4],slice(None))
tlf.tilefigures(figs,[10,1])