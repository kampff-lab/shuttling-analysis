# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import matplotlib.pyplot as plt

def rasterplot(spikes,fmt='b.',offset=0):
    for i in range(len(spikes)):
        plt.plot((i + 1 + offset) * spikes[i],fmt)