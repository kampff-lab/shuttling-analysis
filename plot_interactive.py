# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 16:00:30 2012

@author: IntelligentSystems
"""

import process_session
import image_processing as imgproc


    
def click_logger(figure):
    def ondataclick(x,y):
        print x,y
    click_data_action(figure,ondataclick)