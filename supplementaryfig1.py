# -*- coding: utf-8 -*-
"""
Created on Wed Oct 02 17:50:21 2013

@author: gonca_000
"""

import os
from process_rois import *

output_path = r'C:/figs'
generate_figs = True

# Volume statistics #
barlabels = []
left_volumes = []
right_volumes = []
lesion_order = [0, 2, 6, 5, 1, 4, 3]

####################### Load and Render Functions #############################
    
def load_slices(name,trim_end=None):
    global left_volumes
    global right_volumes
    whole,references = read_whole_slices(name)
    if trim_end is not None:
        whole = whole[0:trim_slices]
        references = references[0:trim_slices]
    left = read_slice(name,'LeftRoiSet',references)
    right = read_slice(name,'RightRoiSet',references)
    left_volumes.append(get_volume_rois(left))
    right_volumes.append(get_volume_rois(right))
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
barlabels.append(label)
bregma_228_pos = 33
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 24 ###########################################
name = 'JPAK_24'
label = 'Lb'
barlabels.append(label)
bregma_228_pos = 32
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 38 ###########################################
name = 'JPAK_38'
label = 'Lc'
barlabels.append(label)
bregma_228_pos = 29
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 36 ###########################################
name = 'JPAK_36'
label = 'Ld'
barlabels.append(label)
bregma_228_pos = 35
sliceline_pos = 36
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos,sliceline_pos)
###############################################################################

########################### JPAK 22 ###########################################
name = 'JPAK_22'
label = 'Le'
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 52 ###########################################
name = 'JPAK_52'
label = 'Lf'
barlabels.append(label)
bregma_228_pos = 36
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 28 ###########################################
name = 'JPAK_28'
label = 'Lg'
barlabels.append(label)
bregma_228_pos = 34
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 48 ###########################################
name = 'JPAK_48'
label = 'Lh'
barlabels.append(label)
bregma_228_pos = 39
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 54 ###########################################
name = 'JPAK_54'
label = 'Li'
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 50 ###########################################
name = 'JPAK_50'
label = 'Lj'
barlabels.append(label)
bregma_228_pos = 37
whole,left,right = load_slices(name)
generate_figures(label,left,right,whole,bregma_228_pos)
###############################################################################

########################### JPAK 26 ###########################################
name = 'JPAK_26'
label = 'Lk'
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
fig = plt.figure()
ax = plt.gca()
r1 = ax.bar(barticks,right_volumes,barwidth,color='orange')
r2 = ax.bar(barticks+barwidth,left_volumes,barwidth,color='purple')
ax.legend((r1[0],r2[0]),('left','right'))
ax.set_xticks(barticks+barwidth)
ax.set_xticklabels(barlabels)
plt.ylabel('lesion volume (mm$^3$)')
plt.savefig(os.path.join(output_path,'lesion_summary.pdf'))
plt.close(fig)
###############################################################################