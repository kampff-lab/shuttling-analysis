# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 05:12:33 2013

@author: IntelligentSystems
"""

import load_data
import plot_session
import matplotlib.pyplot as plt

jp20 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_03_31-18_26', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_01-11_22', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_02-11_16', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_03-11_28', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_04-11_40'],False)
jp21 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_03_31-18_46', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_01-11_57', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_02-11_49', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_03-12_02', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_04-12_14'],False)
jp22 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_07-16_55', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_08-13_53', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_09-13_19', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_10-13_36', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_11-15_20'],False)
jp23 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_07-16_33', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_08-13_19', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_09-12_46', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_10-13_02', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_11-14_46'],False)
jp24 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_14-15_56', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_15-13_07', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_16-12_14', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_17-12_18', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_18-12_12'],False)
jp25 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_14-16_19', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_15-13_41', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_16-12_47', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_17-12_52', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_18-12_46'],False)
jp26 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_21-16_54', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_22-13_59', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_23-14_07', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_24-14_17', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_25-14_15'],False)
jp27 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_21-16_36', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_22-13_23', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_23-13_32', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_24-13_40', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_25-13_39'],False)
jp28 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_04_28-16_59', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_04_29-14_43', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_04_30-14_30', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_01-14_33', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_02-14_35'],False)
jp29 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_04_28-17_18', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_04_29-15_19', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_04_30-15_04', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_01-15_06', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_02-15_09'],False)
jp36 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_07-14_04', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_08-10_43', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_09-10_34', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_10-10_54', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_11-10_44'],False)
jp37 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_07-14_24', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_08-11_18', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_09-11_10', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_10-11_27', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_11-11_18'],False)
jp38 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_07-15_21', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_08-12_37', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_09-12_30', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_10-12_44', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_11-12_36'],False)
jp39 = load_data.load_pathlist([r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_07-14_55', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_08-12_02', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_09-11_56', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_10-12_10', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_11-12_03'],False)

lesions = [jp20,jp22,jp24,jp26,jp28,jp36,jp38]
shams = [jp21,jp23,jp25,jp27,jp29,jp37,jp39]

fig = plt.figure('lesionsham average trial times')
fig.gca().set_color_cycle('r')
plot_session.plot_average_trial_times('lesionsham',lesions[0],'Lesion')
fig.gca().set_color_cycle('b')
plot_session.plot_average_trial_times('lesionsham',shams[0],'Sham')
fig.gca().set_color_cycle('r')
[plot_session.plot_average_trial_times('lesionsham',s,'Lesion') for s in lesions[1:]]
fig.gca().set_color_cycle('b')
[plot_session.plot_average_trial_times('lesionsham',s,'Sham') for s in shams[1:]]
plt.legend(('Lesion','Control'))