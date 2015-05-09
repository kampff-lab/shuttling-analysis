# -*- coding: utf-8 -*-
"""
Created on Wed Oct 02 17:50:21 2013

@author: gonca_000
"""

import os
import pandas as pd
from roiproc import *

output_path = r'C:/figs/histology'
generate_figs = True

# Volume statistics #
barlabels = []
subjects = []
left_volumes = []
right_volumes = []
whole_volumes = []
lesion_order = np.array([0, 4, 12, 10, 2, 18, 8, 14, 20, 16, 6])
control_order = lesion_order+1
# JPAK 20,24,38,36,22,52,28,48,54,50,26

####################### Load and Render Functions #############################
    
def load_slices(name,trim_end=None):
    global left_volumes
    global right_volumes
    global whole_volumes
    whole,references = read_whole_slices(name)
    if trim_end is not None:
        whole = whole[0:trim_end]
        references = references[0:trim_end]
    left = read_slice(name,'LeftRoiSet',references)
    right = read_slice(name,'RightRoiSet',references)
    left_volumes.append(get_volume_rois(left))
    right_volumes.append(get_volume_rois(right))
    whole_volumes.append(get_volume_rois(whole))
    return whole,left,right
    
def generate_figures(name,left,right,whole,bregma_228_pos,sliceline_pos=None):
    if not generate_figs:
        return
        
    dpi = 1200
    zoffset = get_bregma_offset(bregma_228_pos)
    sliceline_pos = bregma_228_pos if sliceline_pos is None else sliceline_pos
    sliceline = (2.28 - (sliceline_pos-bregma_228_pos)*0.1)
    render_top(left,right,whole,zoffset,True,sliceline)
    plt.savefig(os.path.join(output_path,name + '_top.png'),dpi=dpi,bbox_inches='tight', pad_inches=0)
    render_coronal(left,right,whole,zoffset,bregma_228_pos,True)
    plt.savefig(os.path.join(output_path,name + '_coronal.png'),dpi=dpi,bbox_inches='tight', pad_inches=0)
    render_saggital(left,right,whole,zoffset,True)
    plt.savefig(os.path.join(output_path,name + '_saggital.png'),dpi=dpi,bbox_inches='tight', pad_inches=0)
    plt.close('all')
    
########################### JPAK 20 ###########################################
name = 'JPAK_20'
label = 'La'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 33
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 24 ###########################################
name = 'JPAK_24'
label = 'Lb'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 32
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 38 ###########################################
name = 'JPAK_38'
label = 'Lc'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 29
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 36 ###########################################
name = 'JPAK_36'
label = 'Ld'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 35
sliceline_pos = 36
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos,sliceline_pos)
###############################################################################

########################### JPAK 22 ###########################################
name = 'JPAK_22'
label = 'Le'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 52 ###########################################
name = 'JPAK_52'
label = 'Lf'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 36
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 28 ###########################################
name = 'JPAK_28'
label = 'Lg'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 34
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 48 ###########################################
name = 'JPAK_48'
label = 'Lh'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 39
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 54 ###########################################
name = 'JPAK_54'
label = 'Li'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 50 ###########################################
name = 'JPAK_50'
label = 'Lj'
subjects.append(name)
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 26 ###########################################
name = 'JPAK_26'
label = 'Lk'
subjects.append(name)
barlabels.append(label)
trim_slices = 55
bregma_228_pos = 32
sliceline_pos = 36
whole,left,right = load_slices(name,trim_slices)
generate_figures(label,left,right,whole,bregma_228_pos,sliceline_pos)
###############################################################################

########################### SUMMARY ###########################################
barwidth = 0.35
barticks = np.arange(len(left_volumes))
#left_volumes = np.array([l/w for l,w in zip(left_volumes,whole_volumes)])
#right_volumes = np.array([r/w for r,w in zip(right_volumes,whole_volumes)])
fig = plt.figure()
ax = plt.gca()
r1 = ax.bar(barticks,right_volumes,barwidth,color='orange')
r2 = ax.bar(barticks+barwidth,left_volumes,barwidth,color='purple')
#r3 = ax.bar(barticks+barwidth*2,whole_volumes,barwidth,color='gray')
ax.legend((r1[0],r2[0]),('left','right'))
ax.set_xticks(barticks+barwidth)
ax.set_xticklabels(barlabels)
plt.ylabel('lesion volume (mm$^3$)')
plt.savefig(os.path.join(output_path,'lesion_summary.pdf'))
dataset = pd.DataFrame(np.vstack((right_volumes,left_volumes)).T,
                       index=pd.Index(subjects,name='subject'),
                       columns=['lesion_left','lesion_right'])
dataset.to_csv(os.path.join(output_path, 'lesion_volumes.csv'))
plt.close(fig)
###############################################################################