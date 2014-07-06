# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 16:52:58 2013

@author: gonca_000
"""

import numpy as np

def get_video_frame(timestamps,time):
    return np.nonzero(np.genfromtxt(timestamps,dtype=str) == time)[0][0]