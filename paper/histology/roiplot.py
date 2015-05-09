# -*- coding: utf-8 -*-
"""
Created on Wed Oct 02 16:46:52 2013

@author: gonca_000
"""

import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def flatten(l):
    return [item for sublist in l for item in sublist]

def distance_function(point,rois):
    return [np.linalg.norm(np.array(point-roi,dtype=float)) for roi in rois]
    
def point3d(p2d,z,scale,zoffset):
    return [p2d[0]*scale[0],p2d[1]*scale[1],(z*scale[2])+zoffset]

def triangulate_roi(rois,zstep=1,xscale=1,yscale=1,zscale=1,zoffset=0,swapz=False):
    verts = []
    for r,(z,roi) in enumerate(rois):
        nz = z + zstep
        depthstack = flatten([zroi for rz,zroi in rois if rz == z+zstep])
        if len(depthstack) <= 0:
            depthstack = roi
            
        for i,point in enumerate(roi):
            nextpoint = roi[(i + 1) % len(roi)]
            zpoint = depthstack[np.argmin(distance_function(point,depthstack))]
            znextpoint = depthstack[np.argmin(distance_function(nextpoint,depthstack))]
            
            point0 = point3d(zpoint,nz,(xscale,yscale,zscale),zoffset)
            point1 = point3d(point,z,(xscale,yscale,zscale),zoffset)
            point2 = point3d(nextpoint,z,(xscale,yscale,zscale),zoffset)
            point3 = point3d(znextpoint,nz,(xscale,yscale,zscale),zoffset)
            if swapz:
                point0[0], point0[2] = point0[2],point0[0]
                point1[0], point1[2] = point1[2],point1[0]
                point2[0], point2[2] = point2[2],point2[0]
                point3[0], point3[2] = point3[2],point3[0]
            
            verts.append([point0,point1,point2,point3])
    return verts
    
def offset_roi(roi,offset):
    points = roi[1]
    offsetarray = np.tile(offset,(np.shape(points)[0],1))
    roi[1] = points + offsetarray
    
def scale_roi(roi,scale):
    roi[1] = roi[1] * scale
    
def roi_surface(rois,zstep=1,xscale=1,yscale=1,zscale=1,zoffset=0,swapz=False):
    verts = []
    for r,(z,roi) in enumerate(rois):
        for i,point in enumerate(roi):
            nextpoint = roi[(i + 1) % len(roi)]
            point0 = point3d(point,z+zstep,(xscale,yscale,zscale),zoffset)
            point1 = point3d(point,z,(xscale,yscale,zscale),zoffset)
            point2 = point3d(nextpoint,z,(xscale,yscale,zscale),zoffset)
            point3 = point3d(nextpoint,z+zstep,(xscale,yscale,zscale),zoffset)
            if swapz:
                point0[0], point0[2] = point0[2],point0[0]
                point1[0], point1[2] = point1[2],point1[0]
                point2[0], point2[2] = point2[2],point2[0]
                point3[0], point3[2] = point3[2],point3[0]
            
            verts.append([point0,point1,point2,point3])
    return verts
    
def merge_rois(rois,zstep=1):
    rows = []
    z = 0
    for roi in rois:
        for point in roi:
            rows.append([point[0],point[1],z])
        z = z + zstep
    return np.array(rows,dtype=float)

def plot_roi3d(rois,zstep=1,**kwargs):
    ax = plt.gca(projection='3d')
    z = 0
    for roi in rois:
        xs = roi[:,0]
        ys = roi[:,1]
        zs = np.tile(z,(1,len(roi)))
        ax.contour(xs,ys,zs,**kwargs)
        z = z + zstep