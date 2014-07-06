# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 00:55:45 2013

@author: gonca_000
"""

import load_data
import plot_session
import matplotlib.pyplot as plt

def fix_font_size():
    ax = plt.gca()
    plt.tight_layout()
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(18)

folders = [r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38', r'G:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39']

if not 'data' in locals():
    data = load_data.load_path(folders[13])

valid_positions = [200,1000]
plot_session.plot_average_tip_height_end_to_end('dataheight',data,crop=valid_positions,legend=False)
plt.autoscale(enable=True,tight=True)
plt.ylim(-0.5,10)
plt.xlim(xmin=0)
f = plt.gcf()
fix_font_size()
f.savefig(r'G:/symposium/performance/trackingdata/png/jp39_average_tip_height.png',dpi=100)
f.savefig(r'G:/symposium/performance/trackingdata/pdf/jp39_average_tip_height.pdf')
plt.close(f)

plot_session.plot_average_tip_speed_end_to_end('dataspeed',data,crop=valid_positions)
plt.autoscale(enable=True,tight=True)
plt.ylim(ymax=75)
plt.xlim(xmin=0)
f = plt.gcf()
fix_font_size()
f.savefig(r'G:/symposium/performance/trackingdata/png/jp39_average_tip_speed.png',dpi=100)
f.savefig(r'G:/symposium/performance/trackingdata/pdf/jp39_average_tip_speed.pdf')
plt.close(f)