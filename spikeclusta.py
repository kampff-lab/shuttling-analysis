# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 03:20:44 2014

@author: Gonçalo
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.cluster.vq as vq
from numpy import mean,cov,dot,linalg
import lassoselect

def princomp(A):
 """ performs principal components analysis 
     (PCA) on the n-by-p data matrix A
     Rows of A correspond to observations, columns to variables. 

 Returns :  
  coeff :
    is a p-by-p matrix, each column containing coefficients 
    for one principal component.
  score : 
    the principal component scores; that is, the representation 
    of A in the principal component space. Rows of SCORE 
    correspond to observations, columns to components.
  latent : 
    a vector containing the eigenvalues 
    of the covariance matrix of A.
 """
 # computing eigenvalues and eigenvectors of covariance matrix
 M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
 [latent,coeff] = linalg.eig(cov(M)) # attention:not always sorted
 score = dot(coeff.T,M) # projection of the data in the new space
 return coeff,score,latent

class wavecluster:
    def __init__(self, waves, parent, label = None):
        self.waves = waves
        self.parent = parent
        self.label = label
        self.subclusters = None
        self.selected = np.copy(waves.mask)
        
    def getindices(self):
        return np.nonzero(~self.waves.mask[:,0])[0]
        
def loadwaves(filename,wavesize=100):
    waves = np.fromfile(filename,dtype=np.float32)
    waves = waves.reshape((len(waves)/wavesize,wavesize))
    return waves
        
def getvalidrows(maskeddata):
    return maskeddata.view(np.ndarray)[~maskeddata.mask[:,0]]
    
def waveformplot(data,color):
    datashape = np.shape(data)
    mu = np.mean(data,0)
    sd = np.std(data,0)
    x = np.arange(datashape[1])
    plt.title(str.format('count: {0}',datashape[0]))
    plt.plot(mu,color=color)
    plt.fill_between(x,mu-sd,mu+sd,color=color,alpha=0.1)
    plt.xlim(x[0],x[-1])
    
def clustaplot(cluster):
    subclusters = cluster.subclusters
    nclusters = len(subclusters)
    size = np.ceil(np.sqrt(nclusters))
    fig = plt.gcf()
    fig.clear()
    fig.canvas.clustdata = cluster
    for i,clusta in enumerate(subclusters):
        if clusta.label:
            color = mpl.rcParams['axes.color_cycle'][clusta.label]
        else:
            color = 'b'
        ax = plt.subplot(size,size,i+1)
        data = getvalidrows(clusta.waves)
        ax.clustdata = clusta
        waveformplot(data,color)
        
        #plt.plot(mu-sd,'--k')
        #plt.plot(mu+sd,'--k')
    fig.tight_layout()
    
def interclust(waves,k,it=100):
    cid = None
    
    def subcluster(cluster):
        data = getvalidrows(cluster.waves)
        try:
            c,l = vq.kmeans2(data,k,it)
        except:
            l = np.array([i % k for i in range(np.shape(data)[0])])
        result = []
        for i in range(k):
            mask = np.tile(l != i,(np.shape(cluster.waves)[1],1)).T
            fmask = np.tile(True,np.shape(cluster.waves))
            fmask[~cluster.waves.mask[:,0]] = mask
            waves = np.ma.masked_array(cluster.waves,fmask)
            result.append(wavecluster(waves,cluster))
        cluster.subclusters = result
    
    def onclick(event):
        if str.isdigit(str(event.key)):
            clustid = int(event.key)
            event.inaxes.clustdata.label = clustid if clustid > 0 else None
            clusta = event.canvas.clustdata
            clustaplot(clusta)
            updateclusta()
        if event.key == 'q':
            fig.canvas.mpl_disconnect(cid)
        if event.key == 'c':
            clusta = event.inaxes.clustdata
            if clusta.subclusters is None:
                subcluster(clusta)
            clustaplot(clusta)
        if event.key == 'b':
            clusta = event.canvas.clustdata
            if clusta.parent is not None:
                clustaplot(clusta.parent)
        if event.key == 'm':
            clusta = event.canvas.clustdata
            clusta.subclusters = [wavecluster(clusta.waves,clusta)]
            clustaplot(clusta)
        if event.key == 'd':
            clusta = event.canvas.clustdata
            subcluster(clusta)
            clustaplot(clusta)
        if event.key == 'r':
            clusta = event.inaxes.clustdata
            clusta.waves.mask = True
            parent = event.canvas.clustdata
            parent.waves.mask = parent.waves.mask | ~clusta.selected
            clustaplot(parent)
            
    def updateclusta():
        clustafig = plt.figure(1)
        clustax = clustafig.gca()
        clustax.clear()
        for i in range(7):
            data = getwaveforms(root,i)
            color = mpl.rcParams['axes.color_cycle'][i]
            if len(data) > 0:
                waveformplot(data,color)
        plt.figure(0)
        
    def getwaveforms(clusta,label):
        if clusta.label == label:
            return getvalidrows(clusta.waves)
        else:
            data = []
            if clusta.subclusters:
                for subcluster in clusta.subclusters:
                    waveforms = getwaveforms(subcluster,label)
                    if len(waveforms) > 0:
                        data.append(waveforms)
            return np.concatenate(data) if len(data) > 0 else np.array(data)
            

    fig = plt.figure(0)
    cid = fig.canvas.mpl_connect('key_press_event',onclick)
    if not getattr(waves,'subclusters',False):
        maskedwaves = np.ma.masked_array(waves,np.tile(False,np.shape(waves)))
        root = wavecluster(maskedwaves,None)
        subcluster(root)
    else:
        root = waves
    clustaplot(root)
    updateclusta()
    return root
    
def pcaplot(waves):
    coeff,score,latent = princomp(waves)
    data = score[0:2,:].T
    plt.plot(data[:,0],data[:,1],'.')
    return coeff,score,latent
    
def pcaclust(waves):
    colorindex = [0]
    colors = mpl.rcParams['axes.color_cycle']
    coeff,score,latent = princomp(waves)
    data = score[0:3,:].T
    
    def onselect(data,ind):
        ax = plt.subplot(122)
        selectedwaves = waves[ind,:]
        waveformplot(selectedwaves,color=colors[colorindex[0]])
        colorindex[0] = (colorindex[0] + 1) % len(colors)
        
    def onclick(event):
        if event.key == '1':
            ax = plt.subplot(121)
            ax.lman.setdata(data[:,0:2])
        if event.key == '2':
            ax = plt.subplot(121)
            ax.lman.setdata(data[:,0:3:2])
        if event.key == '3':
            ax = plt.subplot(121)
            ax.lman.setdata(data[:,1:3])
        if event.key == 'r':
            ax = plt.subplot(122)
            ax.clear()
            colorindex[0] = 0

    ax = plt.subplot(121)
    #ax.plot(data[:,0],data[:,1],'.')
    ax.lman = lassoselect.LassoManager(ax,data[:,0:2],onselect)
    cid = ax.figure.canvas.mpl_connect('key_press_event',onclick)

    plt.show()