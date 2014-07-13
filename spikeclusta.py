# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 03:20:44 2014

@author: Gonçalo
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
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
        
    def setlabel(self, label):
        self.label = label
        if self.subclusters is not None:
            for cluster in self.subclusters:
                cluster.setlabel(label)
        
    def getindices(self):
        return np.nonzero(~self.waves.mask[:,0])[0]
        
def loadwaves(filename,wavesize=100,dtype=np.float32):
    waves = np.fromfile(filename,dtype)
    waves = waves.reshape((len(waves)/wavesize,wavesize))
    return waves
        
def getvalidrows(maskeddata):
    return maskeddata.view(np.ndarray)[~maskeddata.mask[:,0]]
    
def autocorrelation(times,width):
    result = []
    for i in range(len(times)):
        for j in range(i+1,len(times)):
            delta = times[j] - times[i]
            if delta > width:
                break
            result.append(delta)
            result.append(-delta)
    return result
    
def waveformplot(data,color,Fs=30.0,ax=None,hidex=False,hidey=False):
    if ax is None:
        ax = plt.gca()
    
    datashape = np.shape(data)
    mu = np.mean(data,0)
    sd = np.std(data,0)
    x = np.arange(datashape[1])/Fs
    ax.plot(x,mu,color=color)
    ax.set_title(str.format('count: {0}',datashape[0]))
    ax.fill_between(x,mu-sd,mu+sd,color=color,alpha=0.1)
    ax.set_xlim(x[0],x[-1])
    if not hidex:
        ax.set_xlabel('time (ms)')
    if not hidey:
        ax.set_ylabel('voltage (uv)')

def interclust(time,waves,k,it=100,Fs=30000.0):
    cid = None
    lastax = []
        
    def clustaplot(cluster,subplot_spec=None):
        subclusters = cluster.subclusters
        nclusters = len(subclusters)
        size = int(np.ceil(np.sqrt(nclusters)))
        fig = plt.gcf()
        #fig.clear()
        
        gs = gridspec.GridSpecFromSubplotSpec(size,size,subplot_spec,0.5,0.4)
        addplot = len(lastax) == 0
        fig.canvas.clustdata = cluster
        for i,clusta in enumerate(subclusters):
            if clusta.label:
                color = mpl.rcParams['axes.color_cycle'][clusta.label]
            else:
                color = 'b'
            row = i / size
            col = i % size
            if addplot:
                ax = fig.add_subplot(gs[row,col])
                lastax.append(ax)
            else:
                ax = lastax[i]
                ax.clear()
            data = getvalidrows(clusta.waves)
            ax.clustdata = clusta
            waveformplot(data,color,ax=ax,hidex=row < size-1,hidey=col > 0)
            ax.locator_params(nbins=4)
            
            #plt.plot(mu-sd,'--k')
            #plt.plot(mu+sd,'--k')
        #gs.tight_layout(fig)
        fig.canvas.draw_idle()
    
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
            result.append(wavecluster(waves,cluster,cluster.label))
        cluster.subclusters = result
        
    def matchclusterlabels(clusters,label):
        return np.all(np.array([sc.label == label for sc in clusters]))
    
    def onclick(event):
        if str.isdigit(str(event.key)):
            clustid = int(event.key)
            label = clustid if clustid > 0 else None
            event.inaxes.clustdata.setlabel(label)
            clusta = event.canvas.clustdata
            if matchclusterlabels(clusta.subclusters,label):
                clusta.label = label
            else:
                clusta.label = None
            clustaplot(clusta,clustaplotspec)
            updateclusta()
        if event.key == 'q':
            fig.canvas.mpl_disconnect(cid)
        if event.key == 'c':
            clusta = event.inaxes.clustdata
            if clusta.subclusters is None:
                subcluster(clusta)
            clustaplot(clusta,clustaplotspec)
        if event.key == 'b':
            clusta = event.canvas.clustdata
            if clusta.parent is not None:
                clustaplot(clusta.parent,clustaplotspec)
        if event.key == 'm':
            clusta = event.canvas.clustdata
            clusta.subclusters = [wavecluster(clusta.waves,clusta)]
            clustaplot(clusta,clustaplotspec)
        if event.key == 'd':
            clusta = event.canvas.clustdata
            subcluster(clusta)
            clustaplot(clusta,clustaplotspec)
        if event.key == 'r':
            clusta = event.inaxes.clustdata
            clusta.waves.mask = True
            parent = event.canvas.clustdata
            parent.waves.mask = parent.waves.mask | ~clusta.selected
            clustaplot(parent,clustaplotspec)
            
    def updateclusta():
        maxy = 0
        xlim = timeax.get_xlim()
        clustax.clear()
        timeax.clear()
        isiax.clear()
        autoax.clear()
        timeax.plot(xtime,xtime * 0,'|')
        waveforms = []
        for i in range(7):
            wavedata = getwaveforms(root,i)
            if len(wavedata[0]) > 0:
                waveforms.append((i,wavedata))
        
        for i,(data,datatime) in waveforms:
            chronoind = datatime.argsort()
            data = data[chronoind,:]
            datatime = datatime[chronoind]

            color = mpl.rcParams['axes.color_cycle'][i]
            waveformplot(data,color,ax=clustax)
            timeax.plot(datatime,datatime*0+i,'|',color=color)
            
            isi = np.diff(datatime * 60)
            bins = np.arange(min(isi),max(isi),0.1)
            isiax.hist(isi,bins,color=color,normed=True,alpha=1.0/len(waveforms))
            isiax.set_xlabel('time (s)')
            
            width = 50
            autocorr = autocorrelation(datatime * 60000,width)
            if len(autocorr) > 0:
                bins = np.arange(-width,+width,1)
                autoax.hist(autocorr,bins,color=color)
                autoax.set_xlabel('time (ms)')
                autoax.set_xlim(bins[0],bins[-1])
            
            maxy = i
        timeax.set_xlabel('time (min)')
        if xlim[1] > 1:
            timeax.set_xlim(xlim)
        else:
            timeax.set_xlim(xtime[0],xtime[-1])
        timeax.set_ylim(-1,maxy+1)
        timeax.get_yaxis().set_visible(False)
        
    def getwaveforms(clusta,label):
        if clusta.label == label:
            wavetime = xtime[~clusta.waves.mask[:,0]]
            return getvalidrows(clusta.waves),wavetime
        else:
            data = []
            times = []
            if clusta.subclusters:
                for subcluster in clusta.subclusters:
                    waveforms,wavetime = getwaveforms(subcluster,label)
                    if len(waveforms) > 0:
                        data.append(waveforms)
                        times.append(wavetime)
            if len(data) > 0:
                return np.concatenate(data),np.concatenate(times)
            else:
                return np.array(data),np.array(data)
            
    fig = plt.figure()
    gs0 = gridspec.GridSpec(6, 1,hspace=1)
    gs00 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec = gs0[:-1,:])
    #gs000 = gridspec.GridSpecFromSubplotSpec(6, 1, subplot_spec = gs00[0],hspace=1)
    clustaplotspec = gs00[0]
    
    timeax = fig.add_subplot(gs0[-1])
    xtime = time / (Fs * 60.0)
    
    gs001 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec = gs00[1])
    clustax = fig.add_subplot(gs001[0])
    gs0011 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec = gs001[1])
    isiax = fig.add_subplot(gs0011[0])
    autoax = fig.add_subplot(gs0011[1])
    
    cid = fig.canvas.mpl_connect('key_press_event',onclick)
    if not getattr(waves,'subclusters',False):
        maskedwaves = np.ma.masked_array(waves,np.tile(False,np.shape(waves)))
        root = wavecluster(maskedwaves,None)
        subcluster(root)
    else:
        root = waves
    clustaplot(root,clustaplotspec)
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