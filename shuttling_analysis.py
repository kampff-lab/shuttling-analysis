# -*- coding: utf-8 -*-
"""
Created on Sun Sep 02 16:56:25 2012

@author: IntelligentSystems
"""

import os
import glob
import shutil
import subprocess
import analysis_utilities as utils
import parse_session as parser
import process_session
import numpy as np
import matplotlib as mpl

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
# old bonsai
#    playerpath = dname + r'\bonsai\Bonsai.Player.exe'
# current bonsai
analysisfolder = 'Analysis'
backgroundfolder = 'Background'
playerpath = r'E:\Software\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Player.exe'
editorpath = r'E:\Software\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Editor.exe'

def analysis_pipeline(datafolders):
    
    for path in datafolders:    
        print "Pre-processing "+ path + "..."
        print "Generating crossings..."
        newcrossings = make_crossings(path)
        analysispath = os.path.join(path,analysisfolder)
        currdir = os.getcwd()
        os.chdir(analysispath)
        videoanalysis = os.path.join(dname,'video_analysis.bonsai')
        if newcrossings:
            print "Filtering crossings..."
            subprocess.call([editorpath,videoanalysis,'--start'])
            os.chdir(currdir)
            
    for path in datafolders:
        print "Checking backgrounds for " + path + "..."
        analysispath = os.path.join(path,analysisfolder)
        backgroundsready = make_backgrounds(analysispath)
        if not backgroundsready:
            raise Exception("Aborted due to missing backgrounds!")

    print "Running analysis pipeline..."
    for path in datafolders:
        analysispath = os.path.join(path,analysisfolder)
        shuttling_analysis(analysispath)
    
def background_check(path):
    crossings_filename = os.path.join(path,'crossings.csv')
    crossings = utils.ensure_list(np.genfromtxt(crossings_filename,dtype=str))
    if len(crossings) > 0:        
        backgroundpath = os.path.join(path,backgroundfolder)
        backgroundfiles = sorted(os.listdir(backgroundpath))
        if len(backgroundfiles) == 0:
            # There are no backgrounds!
            return (False,None)
            
        last_crossing = crossings[-1]
        last_background = os.path.splitext(backgroundfiles[-1])[0]
        separator = last_background.find('_') + 1
        last_background = last_background[separator:].replace('_',':')
        return (last_background > last_crossing,last_crossing.replace(':','_'))
    return (True,None)

def make_crossings(path="."):
    if not isinstance(path,basestring):
        for p in path:
            make_crossings(p)
        return True
    
    analysispath = os.path.join(path,analysisfolder)
    filename = os.path.join(analysispath,'crossings.csv')
    timestamp_filename = os.path.join(path,'front_video.csv')
    activity_filename = os.path.join(path,'center_activity.csv')
    if os.path.exists(filename):
        ans = raw_input('File exists - overwrite? (y/n)')
        if ans != 'y':
            return False
    
    if not os.path.exists(timestamp_filename):
        return False
    
    if not os.path.exists(analysispath):
        os.mkdir(analysispath)
        
    timestamps = np.genfromtxt(timestamp_filename,usecols=0,dtype=str)
    if os.path.exists(activity_filename):
        area = np.genfromtxt(activity_filename)
    else:
        area = np.genfromtxt(timestamp_filename,usecols=4)
    
    crosses = np.insert(np.diff(np.array(area > 500000,dtype=int)),0,0)
    cross_in = mpl.mlab.find(crosses > 0)
    cross_out = mpl.mlab.find(crosses < 0)
    ici = cross_in[1:] - cross_out[0:len(cross_out)-1]
    valid_crosses = np.insert(ici > 120,0,True)
    cross_times = timestamps[cross_in[valid_crosses]]
    np.savetxt(filename,cross_times,'%s')
    return True
    
def make_backgrounds(path=None):
    currdir = os.getcwd()
    if path is not None:
        os.chdir(path)
    
    if os.path.exists(backgroundfolder):
        ans = raw_input('Backgrounds exist - overwrite? (y/n)')
        if ans != 'y':
            return True
        else:
            shutil.rmtree('Background')
        
    backgroundbuilder = dname + r'\background_builder_v2.bonsai'
    print "Extracting raw backgrounds..."
    subprocess.call([playerpath, backgroundbuilder])
    validbackgrounds,lastcrossing = background_check(path)
    if not validbackgrounds:
        print "Found crossings with no matching background!"
        ans = raw_input('Last crossing is %s - proceed? (y/n)' % (lastcrossing))
        if ans != 'y':
            return False
                
    os.chdir(currdir)
    return True

def remove_file(path):
    for filename in glob.glob(path):
        os.remove(filename)
        
def delete_video_analysis(path=None):
    currdir = os.getcwd()
    if path is not None:
        os.chdir(path)
        
    if os.path.exists('mean.csv') or os.path.exists('step0.csv'):
        print "Deleting existing data..."
        remove_file('mean.csv')
        remove_file('centroid_x.csv')
        remove_file('centroid_y.csv')
        remove_file('step*.csv')
        remove_file('tip_horizontal.csv')
        remove_file('tip_vertical.csv')
        remove_file('trial_time.csv')
        
    os.chdir(currdir)

def refresh_analysis(datafolders=None):
    if datafolders is None:
#        basefolder = 'F:\Protocols\Shuttling\Data'
#        basefolder = r'F:\Protocols\Behavior\Shuttling\LightDarkFixed\Data'
#        datafolders = [path + '\\Analysis' for path in utils.flatten(utils.directory_tree(basefolder,2))]
#        
#        basefolder = r'F:\Protocols\Behavior\Shuttling\LightDarkVariable\Data'
#        datafolders += [path + '\\Analysis' for path in utils.flatten(utils.directory_tree(basefolder,2))]
        # manual overwrite of datafolder to run only on reanalyzed files
        f = open(r'C:\Users\IntelligentSystems\Documents\Insync\kampff.lab@gmail.com\users\tschroder\analysis_filelist.txt')
        datafolders = [x.rstrip('\n') for x in f]        
        
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
    
    delete_video_analysis()
#==============================================================================
#    if os.path.exists('mean.csv') or os.path.exists('step0.csv'):
#        print "Deleting existing data..."
#        remove_file('mean.csv')
#        remove_file('centroid_x.csv')
#        remove_file('centroid_y.csv')
#        remove_file('step0.csv')
#        remove_file('step1.csv')
#        remove_file('step2.csv')
#        remove_file('step3.csv')
#        remove_file('step4.csv')
#        remove_file('step5.csv')
#        remove_file('tip_horizontal.csv')
#        remove_file('tip_vertical.csv')
#        remove_file('trial_time.csv')
#==============================================================================

#    if not os.path.exists(backgroundfolder):
#        backgroundbuilder = dname + r'\background_builder_v2.bonsai'
#        print "Extracting raw backgrounds..."
#        subprocess.call([playerpath, backgroundbuilder])
#        if not background_check(path):
#            print "Found crossings with no matching background!"
#            proceed = input('Proceed?')
#            if not isinstance(proceed,bool) or not proceed:
#                raise Exception("Aborted by user!")
    
#==============================================================================
#     if not os.path.exists('crossings_cleaned.csv'):
#         print "Cleaning crossings"
#         crossclean = dname + r'\crossing_autocorrection.bonsai'
#         subprocess.call([playerpath_new, crossclean])
#     
#     if os.path.exists('crossings_cleaned.csv'):
#         os.rename('crossings.csv', 'crossings_old.csv')
#         os.rename('crossings_cleaned.csv', 'crossings.csv')
#         
#     shutil.rmtree('Background')
#     if not os.path.exists('Background'):
#         backgroundbuilder = dname + r'\background_builder_v2.bonsai'
#         print "Extracting backgrounds..."
#         subprocess.call([playerpath_new, backgroundbuilder])
#==============================================================================

    if not os.path.exists('mean.csv'):
        videoprocessing = dname + r'\video_processing_tip_servo_lightbox.bonsai'
        print "Analysing crossing videos..."
        subprocess.call([playerpath, videoprocessing])

#==============================================================================
#     if not os.path.exists('mean.csv'):
#         videoprocessing = dname + r'\video_processing_tip_steppers.bonsai'
#         print "Analysing crossing videos..."
#         subprocess.call([playerpath, videoprocessing])
#         
#     stepfile = 'step0_times.csv'
#     if not os.path.exists(stepfile) or os.stat(stepfile).st_size == 0 or True:
#         print "Extracting step times..."
#         session = parser.parse_session(path,path,True)
#         process_session.make_step_times(session)
#         print "Saving step frames..."
#         buildsteppath = dname + r'\steps\build_step_frames'
#         os.system(buildsteppath)
#         print "Saving average step frames..."
#         process_session.make_step_means(session)
#==============================================================================
#        del session

    stepfile = 'step0_times.csv'
    if not os.path.exists(stepfile) or os.stat(stepfile).st_size == 0 or True:
        print "Extracting step times..."
        session = parser.parse_session(path,path,True)
        process_session.make_step_times(session)
        print "Saving step frames..."
        buildsteppath = dname + r'\stepper_steps\build_step_frames'
        os.system(buildsteppath)
        print "Saving average step frames..."
        process_session.make_step_means(session)

    os.chdir(currdir)