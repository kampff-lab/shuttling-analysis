# -*- coding: utf-8 -*-
"""
Created on Sun Sep 02 16:56:25 2012

@author: IntelligentSystems
"""

import os
import subprocess
import analysis_utilities as utils
import parse_session as parser
import process_session

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

def remove_file(path):
    if os.path.exists(path):
        os.remove(path)

def refresh_analysis():
    basefolder = 'F:\Protocols\Shuttling\Data'
    datafolders = [path + '\\Analysis' for path in utils.flatten(utils.directory_tree(basefolder,2))]
    for path in datafolders:
        try:
            shuttling_analysis(path)
        except Exception, e:
            print "Failed to process '" + path + "' with error: %s!" % e

def shuttling_analysis(path):
    if not os.path.exists(path):
        return
    
    global dname
    currdir = os.getcwd()
    print "Processing "+ path + "..."
    os.chdir(path)
    
#==============================================================================
#     if os.path.exists('mean.csv') or os.path.exists('step0.csv'):
#         print "Deleting existing data..."
#         remove_file('mean.csv')
#         remove_file('centroid_x.csv')
#         remove_file('centroid_y.csv')
#         remove_file('step0.csv')
#         remove_file('step1.csv')
#         remove_file('step2.csv')
#         remove_file('step3.csv')
#         remove_file('step4.csv')
#         remove_file('step5.csv')
#         remove_file('tip_horizontal.csv')
#         remove_file('tip_vertical.csv')
#         remove_file('trial_time.csv')
#==============================================================================

    playerpath = dname + r'\bonsai\Bonsai.Player.exe'        
    if not os.path.exists('Background'):
        backgroundbuilder = dname + r'\background_builder.bonsai'        
        print "Extracting backgrounds..."
        subprocess.call([playerpath, backgroundbuilder])
    
    if not os.path.exists('mean.csv'):
        videoprocessing = dname + r'\video_processing.bonsai'
        print "Analysing crossing videos..."
        subprocess.call([playerpath, videoprocessing])
        
    stepfile = 'step0_times.csv'
    if not os.path.exists(stepfile) or os.stat(stepfile).st_size == 0 or True:
#        print "Extracting step times..."
        session = parser.parse_session(path,path,False,True)
#        process_session.make_step_times(session)
#        print "Saving step frames..."
#        buildsteppath = dname + r'\steps\build_step_frames'
#        os.system(buildsteppath)
        print "Saving average step frames..."
        process_session.make_step_means(session)
        del session
    os.chdir(currdir)