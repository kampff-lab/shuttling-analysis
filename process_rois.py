# -*- coding: utf-8 -*-
"""
Created on Wed Oct 09 00:38:31 2013

@author: gonca_000
"""

import os
import polygon
import read_roi
import plot_rois
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d
default_proj = proj3d.persp_transformation
default_invproj = proj3d.inv_transform
def ortho_invproj(xd,yd,z,M):
    return 0,0,0
def orthogonal_proj(zfront, zback):
    a = (zfront+zback)/(zfront-zback)
    b = -2*(zfront*zback)/(zfront-zback)
    return np.array([[1,0,0,0],
                        [0,1,0,0],
                        [0,0,a,b],
                        [0,0,0,zback]])
proj3d.persp_transformation = orthogonal_proj
proj3d.inv_transform = ortho_invproj

left_color = 'purple'
right_color = 'orange'
pixels_per_mm = 1 / (0.09376746366685201554698035976287 * 1000)
storage_base = r'C:/Analysis/'
#storage_base = r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/'

def swap_xy(rois):
    for roi in rois:
        roi[1][:,[0,1]] = roi[1][:,[1,0]]

def mix_reference_xy(referencey,referencex):
    return [np.array([rx[0],ry[1]]) for rx,ry in zip(referencex,referencey)]

def get_minheightpoints(rois):
    return [ps[np.argmin([p[0] for p in ps])] for z,ps in rois]

def get_centroids(rois):
    return [polygon.centroid(roi[1]) for roi in rois]

def center_rois(rois,references):
    for roi in rois:
        plot_rois.offset_roi(roi,-references[roi[0]-1])
        
def scale_rois(rois,scale):
    for roi in rois:
        plot_rois.scale_roi(roi,scale)

def render_rois(volumes,colors,triangulate=False,zstep=-1,xscale=1,yscale=1,zscale=-0.1,zoffset=0,swapz=False):
    if triangulate:
        verts = [plot_rois.triangulate_roi(volume,zstep,xscale,yscale,zscale,zoffset,swapz) for volume in volumes]
    else:
        verts = [plot_rois.roi_surface(volume,zstep,xscale,yscale,zscale,zoffset,swapz) for volume in volumes]
    
    ax = plt.gca(projection='3d')
    for v,c in zip(verts,colors):
        ax.add_collection3d(Poly3DCollection(v,facecolors=c,edgecolors=[0,0,0,0]))
    ax.set_xlim(-700 * pixels_per_mm,700 * pixels_per_mm)
    ax.set_ylim(-700 * pixels_per_mm,700 * pixels_per_mm)
    ax.set_zlim(0,-60*zscale)
    return ax
    
def render_top(left,right,whole,zoffset,smooth=True,sliceline=None):
    plt.figure()
    ax = render_rois([left,right,whole],[left_color,right_color,[0,0,0,0.2]],smooth,zoffset=zoffset)
    if sliceline is not None:
        ax.plot([0,0],plt.ylim(),[sliceline,sliceline],'k',linewidth=2)
    ax.view_init(elev=0,azim=-180)
    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.set_ylabel('\nML (mm)',linespacing=2.4)
    ax.set_zlabel('AP (mm)')
    ylabels = np.array(np.abs(ax.get_yticks()+2),dtype=np.int)
    ax.set_yticklabels(ylabels)
    plt.draw()
    
def render_coronal(left,right,whole,zoffset,slicecut,smooth=True):
    plt.figure()
    ax = render_rois([left,right,whole[slicecut:]],[left_color,right_color,[0,0,0,0.2]],smooth,zoffset=zoffset,yscale=-1)
    ax.view_init(elev=90,azim=0)
    ax.set_zticks([])
    ax.set_zticklabels([])
    ax.set_xlabel('DV (mm)')
    ax.set_ylabel('\nML (mm)',linespacing=2.4)
    ax.set_xlim(-3,11)
    ylabels = np.array(np.abs(ax.get_yticks()+2),dtype=np.int)
    ax.set_yticklabels(ylabels)
    plt.draw()

def render_saggital(left,right,whole,zoffset,smooth=True):
    plt.figure()
    ax = render_rois([left,right,whole],[left_color,right_color,[0,0,0,0.2]],smooth,zoffset=zoffset,swapz=True)
    ax.view_init(elev=-180,azim=-90)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xlabel('AP (mm)')
    ax.set_zlabel('DV (mm)')
    ax.set_xlim(0,6)
    ax.set_ylim(-700 * pixels_per_mm,700 * pixels_per_mm)
    ax.set_zlim(-3,11)
    ylabels = np.array(np.abs(ax.get_yticks()+2),dtype=np.int)
    ax.set_yticklabels(ylabels)
    plt.draw()
    
def read_whole_slices(sid):
    whole = read_roi.read_roi_zip(os.path.join(storage_base,str.format('protocols/shuttling/slices/{0}/{0}_WholeBrainRoiSet.zip',sid)))
    references = get_centroids(whole)
    maxheightpoints = get_minheightpoints(whole)
    mixref = mix_reference_xy(references,maxheightpoints)
    center_rois(whole,mixref)
    scale_rois(whole,pixels_per_mm)
    return whole,mixref
    
def read_slice(sid,name,references):
    rois = read_roi.read_roi_zip(os.path.join(storage_base,str.format('protocols/shuttling/slices/{0}/{0}_{1}.zip',sid,name)))
    center_rois(rois,references)
    scale_rois(rois,pixels_per_mm)
    return rois
    
def get_bregma_offset(bregma_228_pos):
    return 2.28 + ((bregma_228_pos-1)*0.1)
    
def get_volume_rois(rois):
    volume = 0
    for z,poly in rois:
        volume += abs(polygon.area_for_polygon(poly)) * 0.1
    return volume