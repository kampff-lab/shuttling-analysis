# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 20:47:07 2014

@author: IntelligentSystem
"""

import cv2
import numpy as np

def boundingbox(points):
    minx = None
    maxx = None
    miny = None
    maxy = None
    for x,y in points:
        if minx is None:
            minx = x
            maxx = x
            miny = y
            maxy = y
        else:
            minx = min(minx,x)
            maxx = max(maxx,x)
            miny = min(miny,y)
            maxy = max(maxy,y)
    return (minx,maxx),(miny,maxy)
    
def centroid(points):
    cx = 0
    cy = 0
    for x,y in points:
        cx += x
        cy += y
    cx /= len(points)
    cy /= len(points)
    return cx,cy
    
def croprect(centroid,shape,frame):
    halfh = shape[0] / 2
    halfw = shape[1] / 2
    top = max(0,centroid[0] - halfh)
    bottom = min(frame.shape[0]-1,centroid[0] + halfh)
    left = max(0,centroid[1] - halfw)
    right = min(frame.shape[1]-1,centroid[1] + halfw)
    return frame[slice(top,bottom),slice(left,right)]
    
import video
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as hier
    
def distancematrix(frames,normType=cv2.cv.CV_L2):
    result = np.zeros((len(frames),len(frames)))
    for i in xrange(len(frames)):
        for j in xrange(i,len(frames)):
            distance = cv2.norm(frames[i],frames[j],normType)
            result[i,j] = distance
            if i != j:
                result[j,i] = distance
    return result
    
def cluster(frames,vid=None,indices=None):
    fig = plt.figure()
    distance = distancematrix(frames,cv2.cv.CV_L1)
    Z = hier.linkage(distance,'complete')
    ax1 = plt.subplot2grid((3,2),(1,0), rowspan=2)
    
    #im = ax1.imshow(distance)
    #plt.colorbar(im, ax=ax1)
    
    ax2 = plt.subplot2grid((3,2),(0,0))
    R = hier.dendrogram(Z)
    leaves = R['leaves']
    sframes = frames[leaves]
    
    distance = distancematrix(sframes,cv2.cv.CV_L1)
    im = ax1.imshow(distance)
    plt.colorbar(im, ax=ax1)
    
    fn,fm = sframes[0].shape
    ax3 = plt.subplot2grid((3,2),(0,1), rowspan=3)
    ntiles = int(np.ceil(np.sqrt(len(frames))))
    tiles = tile(sframes,ntiles,ntiles)
    ax3.imshow(tiles[0])
    
#    artists = []
#    def onmouseclick(evt):
#        if evt.inaxes == ax2:        
#            clusters = hier.fcluster(Z,evt.ydata,'distance')
#            sframes = frames[np.argsort(clusters)] if np.max(clusters) > 1 else frames
#            rtiles = tile(sframes,ntiles,ntiles)
#            tiles[0] = rtiles[0]
#            ax3.imshow(tiles[0])
#            fig.canvas.draw_idle()
#            
#        if evt.inaxes == ax3:
#            x = int(evt.xdata / fm)
#            y = int(evt.ydata / fn)
#            fi = y * ntiles + x
#            if vid is not None and indices is not None:
#                idx = indices[leaves[fi]]
#                video.showmovie(vid,idx)
#    
#    def onmousemove(evt):
#        while len(artists) > 0:
#            fig.canvas.draw_idle()
#            artist = artists.pop()
#            artist.remove()
#            
#        if evt.inaxes == ax2:
#            y = evt.ydata
#            xmin,xmax = ax2.get_xlim()
#            artists.append(ax2.hlines(y,xmin,xmax))
#            fig.canvas.draw_idle()
#    h1 = fig.canvas.mpl_connect('motion_notify_event',onmousemove)
#    h2 = fig.canvas.mpl_connect('button_press_event',onmouseclick)
    
    plt.tight_layout()
#    return h1,h2

def tile(frames,width,height,labels=None):
    frameshape = np.shape(frames[0])
    frametype = frames[0].dtype

    pages = []
    pagecount = width * height
    npages = len(frames) / pagecount
    npages = npages + 1 if len(frames) % pagecount != 0 else npages
    for i in range(npages):
        page = np.zeros((frameshape[0] * height,frameshape[1] * width),frametype)
        for k in range(pagecount):
            fi = i * pagecount + k
            if fi >= len(frames):
                continue
            
            frame = frames[fi]
            if labels is not None:
                frame = frame.copy()
                cv2.putText(frame,labels[fi],(0,frame.shape[0]-1),
                            cv2.cv.CV_FONT_HERSHEY_COMPLEX,1,
                            (255,255,255,255))
            offsetH = int(k / width) * frameshape[0]
            offsetW = int(k % width) * frameshape[1]
            sliceH = slice(offsetH,offsetH + frameshape[0])
            sliceW = slice(offsetW,offsetW + frameshape[1])
            page[sliceH,sliceW] = frame
        pages.append(page)
    return pages
    
def crop(frames,xslice,yslice):
    return [frame[yslice,xslice] for frame in frames]
    
def calcpca(data):
    U, s, Vt = np.linalg.svd(data,full_matrices=False)
    V = Vt.T
    
    # sort the PCs by descending order of the singular values (i.e. by the
    # proportion of total variance they explain)
    ind = np.argsort(s)[::-1]
    U = U[:, ind]
    s = s[ind]
    V = V[:, ind]
    return U, s, V
    
def pca(X):
  # Principal Component Analysis
  # input: X, matrix with training data as flattened arrays in rows
  # return: projection matrix (with important dimensions first),
  # variance and mean

  #get dimensions
  num_data,dim = X.shape

  #center data
  mean_X = X.mean(axis=0)
  for i in range(num_data):
      X[i] -= mean_X

  if dim>100:
      M = np.dot(X,X.T) #covariance matrix
      e,EV = np.linalg.eigh(M) #eigenvalues and eigenvectors
      tmp = np.dot(X.T,EV).T #this is the compact trick
      V = tmp[::-1] #reverse since last eigenvectors are the ones we want
      S = np.sqrt(e)[::-1] #reverse since eigenvalues are in increasing order
  else:
      U,S,V = np.linalg.svd(X)
      V = V[:num_data] #only makes sense to return the first num_data

  #return the projection matrix, the variance and the mean
  return V,S,mean_X