# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 17:47:45 2013

@author: gonca_000
"""

import os
import glob
import shutil
import filecmp
import dateutil
import subprocess
import numpy as np

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

analysisfolder = 'Analysis'
backgroundfolder = 'Background'
playerpath = os.path.join(dname, r'../bonsai.lesions/Bonsai.Player.exe')

def process_subjects(datafolders,preprocessing=True,overwrite=False):
    for basefolder in datafolders:
        datafolders = [path for path in directorytree(basefolder,1)]
        process_sessions(datafolders,preprocessing,overwrite)
        
def process_sessions(datafolders,preprocessing=True,overwrite=None):
    
    if preprocessing:
        print 'Generating labels...'
        make_sessionlabels(datafolders)

        # Check for front activity file and regenerate if necessary        
        for path in datafolders:
            make_analysisfolder(path)
            front_activity_path = os.path.join(path,'front_activity.csv')
            if not os.path.exists(front_activity_path):
                analysispath = os.path.join(path,analysisfolder)
                os.chdir(analysispath)
                print 'Generating front activity data...'
                activitydetector = os.path.join(dname,'bonsai/video_activity_detector.bonsai')
                subprocess.call([playerpath,activitydetector])
        
        # Check for background files and regenerate if necessary        
        for path in datafolders:
            print "Checking backgrounds for " + path + "..."
            analysispath = os.path.join(path,analysisfolder)
            backgroundsready = make_backgrounds(analysispath,overwrite)
            if not backgroundsready:
                raise Exception("Aborted due to missing backgrounds!")

    print "Running analysis pipeline..."
    for path in datafolders:
        analysispath = os.path.join(path,analysisfolder)
        make_videoanalysis(analysispath)

def sessionlabel(path):
    protocolfilefolder = os.path.join(dname,'../protocolfiles/lesionsham')
    trialfiles = [f for f in glob.glob(path + r'\step*_trials.csv')]
    for folder in os.listdir(protocolfilefolder):
        match = True
        targetfolder = os.path.join(protocolfilefolder,folder)
        for f1,f2 in zip(trialfiles,os.listdir(targetfolder)):
            targetfile = os.path.join(targetfolder,f2)
            if not filecmp.cmp(f1,targetfile):
                match = False
                break
        
        if match:
            return folder
    return None

def make_sessionlabels(datafolders):
    for path in datafolders:
        label = sessionlabel(path)
        session_labels_file = os.path.join(path,'session_labels.csv')
        if not os.path.exists(session_labels_file):
            np.savetxt(session_labels_file,[['protocol',label]],delimiter=':',fmt='%s')
            
def make_analysisfolder(path):
    analysispath = os.path.join(path,analysisfolder)
    if not os.path.exists(analysispath):
        print "Creating analysis folder..."
        os.mkdir(analysispath)

def make_backgrounds(path=None,overwrite=None):
    currdir = os.getcwd()
    if path is not None:
        os.chdir(path)
    
    if os.path.exists(backgroundfolder):
        if overwrite is None:
            overwrite = raw_input('Backgrounds exist - overwrite? (y/n)')
        if overwrite != 'y':
            return True
        else:
            shutil.rmtree('Background')
        
    backgroundbuilder = os.path.join(dname, r'bonsai/background_builder.bonsai')
    print "Extracting raw backgrounds..."
    subprocess.call([playerpath, backgroundbuilder])
    os.chdir(currdir)
    return True
    
def make_videoanalysis(path):
    if not os.path.exists(path):
        return
    
    global dname
    currdir = os.getcwd()
    print "Processing "+ path + "..."
    os.chdir(path)
    
    if not os.path.exists('trajectories.csv'):
        videoprocessing = os.path.join(dname, r'bonsai/video_preprocessor.bonsai')
        print "Analysing video frames..."
        subprocess.call([playerpath, videoprocessing])
        
    videotimepath = 'videotime.csv'
    if not os.path.exists(videotimepath):
        frametimespath = os.path.join(path, '../front_video.csv')
        frametimes = np.genfromtxt(frametimespath,dtype=str)
        print "Generating relative frame times..."
        datetimes = [dateutil.parser.parse(timestr) for timestr in frametimes]
        videotime = [(time - datetimes[0]).total_seconds() for time in datetimes]    
        np.savetxt(videotimepath, np.array(videotime), fmt='%s')

    os.chdir(currdir)
    
def directorytree(path,level):
    if level > 0:
        return [directorytree(path + '\\' + name, level-1) for name in os.listdir(path)]
    return path