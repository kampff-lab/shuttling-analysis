# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 16:47:56 2013

@author: gonca_000
"""

import video_player
datafolder = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/'

### MANIPULATION VIDEOS ###
clip_duration = 5*120
video_player.play_video_data(datafolder+'JPAK_20/2013_04_05-11_47/front_video.avi','',0,62732,62732+clip_duration,True)