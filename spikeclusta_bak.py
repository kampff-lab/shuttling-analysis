# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 03:20:44 2014

@author: Gonçalo
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.cluster.vq as vq

class spcluster:
    def __init__(self, parent, clusta, owner, label):
        self.parent = parent
        self.clusta = clusta
        self.owner = owner
        self.label = label

def clusta(waves):
    c,l = vq.kmeans2(waves,10,100)
    
def clustaplot(waves,k,label,parent=None):
    size = np.ceil(np.sqrt(k))
    fig = plt.gcf()
    for i in range(k):
        clusta = waves[label == i,:]
        mu = np.mean(clusta,0)
        sd = np.std(clusta,0)
        ax = plt.subplot(size,size,i+1)
        ax.clear()
        ax.clustdata = spcluster(parent,clusta,waves,label)
        plt.title(str.format('count: {0}',np.shape(clusta)[0]))
        plt.plot(mu)
        plt.plot(mu-sd,'--k')
        plt.plot(mu+sd,'--k')
    fig.tight_layout()
    
def interclust(waves,k,it=100):
    cid = None
    
    def onclick(event):
        if event.key == 'q':
            fig.canvas.mpl_disconnect(cid)
        if event.key == 'c':
            clusta = event.inaxes.clustdata.clusta
            c,l = vq.kmeans2(clusta,k,it)
            clustaplot(clusta,k,l,event.inaxes.clustdata)
        if event.key == 'b':
            parent = event.inaxes.clustdata.parent
            if parent is not None:
                clustaplot(parent.owner,k,parent.label,parent.parent)
    
    fig = plt.figure()
    cid = fig.canvas.mpl_connect('key_press_event',onclick)
    c,l = vq.kmeans2(waves,k,it)
    clustaplot(waves,k,l)