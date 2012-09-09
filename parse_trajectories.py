# -*- coding: utf-8 -*-
"""
Created on Mon May 14 10:50:23 2012

@author: IntelligentSystems
"""

import csv
import string
import numpy as np

crossings = []
session = csv.reader(open('crossings.csv', 'rb'), delimiter=' ')
for trial in session:
    trajectory = []
    for point in trial:
        parray = [float(n) for n in string.split(point, sep=';')]
        trajectory.append(parray)
    crossings.append(np.array(trajectory))