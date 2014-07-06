# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:37:24 2013

@author: gonca_000
"""

import load_data
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import plot_utilities as pltutils
import figure_utilities as figutils
import process_trajectories as proctraj

plt.close('all')

# Set Base Path
base_path = r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com'
#base_path = r'C:\kampff\Insync\kampff.lab@gmail.com'
#base_path = r'D:\kampff\Insync\kampff.lab@gmail.com'
#base_path = r'C:\kampff\Insync'

# Set Figure Directory
saveDirectory = r'C:\Users\gonca_000\Desktop\All Trajectories'

# Load and process the 'pickled' Trajectories (Week 3 only)
if not 'experiment' in locals():
    experiment = load_data.load_pickle(base_path + r'\protocols\shuttling\data\trajectories_week3.pickle')

# Set Animal
#animals = [1, 4, 5, 12, 13, 2, 3, 10, 11, 8, 9, 6, 7]
#names = ['Ca', 'Lb', 'Cb', 'Lc', 'Cc', 'Ld', 'Cd' ,'Le', 'Ce', 'Lf', 'Cf', 'Lg', 'Cg']

# Set Trial Validation Directory
validationpath = base_path + r'\protocols\shuttling\ARK\MC Lesion-Sham Analysis\Figures\Figure 3\Valid Trials'

############# Figure 3b - Example Profiles ######################
animals = [4, 5]
names = ['Lb', 'Cb']
sessions = [1, 2, 3]

profiles = [figutils.get_randomized_speed_profiles(experiment,a,sessions,validationpath) for a in animals]
[figutils.plot_randomized_speed_profiles(avgSpeeds,trialTypes) for avgSpeeds,trialTypes in profiles]

############# Figure 3c - Average Group Profiles ######################
animals = [1, 5, 13, 3, 11, 9, 7, 4, 12, 2, 10, 8, 6] # Remove JP20 (never crossed)
sessions = [1,2,3]

# Compute speed profiles for all sessions for each animal
control_profiles = [figutils.get_randomized_speed_profiles(experiment,a,sessions,validationpath) for a in animals[0:7]]
lesion_profiles = [figutils.get_randomized_speed_profiles(experiment,a,sessions,validationpath) for a in animals[7:]]

# Compute average speed profiles for all of the above
control_average_profiles = figutils.get_randomized_group_average_speed_profiles(control_profiles)
lesion_average_profiles = figutils.get_randomized_group_average_speed_profiles(lesion_profiles)

#ax = plt.subplot(111)
## Turn off axis lines and ticks of the big subplot
#ax.spines['top'].set_color('none')
#ax.spines['bottom'].set_color('none')
#ax.spines['left'].set_color('none')
#ax.spines['right'].set_color('none')
#ax.set_axis_bgcolor('none')
#ax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
#plt.ylabel('normalized horizontal speed')
fig = plt.figure()
ax1 = plt.subplot(211)
figutils.plot_randomized_group_average_speed_profiles(control_average_profiles,title='Control Subjects, n = 7',labelx=False,labely=True,legend=True)
plt.ylabel('')
plt.setp( ax1.get_xticklabels(), visible=False)
ax2 = plt.subplot(212,sharex=ax1,sharey=ax1)
figutils.plot_randomized_group_average_speed_profiles(lesion_average_profiles,title='Lesion Subjects, n = 6',labely=True,legend=False)
plt.ylabel('')
plt.figtext(0.01,0.72,'normalized horizontal speed',rotation='vertical',fontsize=15)

############# Figure 3d - Average Group Profiles ######################
controls = []
lesions = []

#for s in sessions:
# Compute Control average difference between stable and unstable for all of the above
diff,error,mean_diff = figutils.get_randomized_group_speed_profile_difference(control_average_profiles)
controls.append(mean_diff)

# Compute Lesion average difference between stable and unstable for all of the above
diff,error,mean_diff = figutils.get_randomized_group_speed_profile_difference(lesion_average_profiles)
lesions.append(mean_diff)

plt.figure(figsize=(4,7))
figutils.plot_randomized_speed_profile_difference_comparison(controls,lesions)