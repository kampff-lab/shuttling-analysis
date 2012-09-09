# -*- coding: utf-8 -*-
"""
Created on Tue May 22 16:41:21 2012

@author: IntelligentSystems
"""

import cv
import os
import glob

count = 0
average = None
path = 'Clips/'

for infile in glob.glob(os.path.join(path, '*.bmp')):
    image = cv.LoadImage(infile, False)
    if average is None:
        average = cv.CreateImage(cv.GetSize(image), 32, 1)
        image_aux = cv.CloneImage(average)
        cv.Convert(image, average)
    else:
        count = count + 1
        scale = 1 / count
        cv.Convert(image, image_aux)
        cv.Sub(image_aux, average, image_aux)        
        cv.Scale(image_aux, image_aux, scale)
        cv.Add(average, image_aux, average)

cv.Convert(average, image)
cv.SaveImage('background.bmp', image)