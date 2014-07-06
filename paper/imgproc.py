# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 20:47:07 2014

@author: IntelligentSystem
"""

import numpy as np

def tile(frames,pagex,pagey):
    frameshape = np.shape(frames[0])
    frametype = frames[0].dtype

    pages = []
    pagecount = pagex * pagey
    npages = len(frames) / pagecount if pagecount < len(frames) else len(frames)
    for i in range(npages):
        page = np.zeros((frameshape[0] * pagex,frameshape[1] * pagey),frametype)
        for k in range(pagecount):
            fi = i * pagecount + k
            if fi >= len(frames):
                continue
            
            frame = frames[fi]
            offsetX = int(k % pagex) * frameshape[0]
            offsetY = int(k / pagex) * frameshape[1]
            sliceX = slice(offsetX,offsetX + frameshape[0])
            sliceY = slice(offsetY,offsetY + frameshape[1])
            page[sliceX,sliceY] = frame
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