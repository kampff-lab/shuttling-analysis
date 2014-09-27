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
import datetime
import subprocess
import numpy as np
import pandas as pd

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

fronttime_key = 'video/front/time'
frontactivity_key = 'video/front/activity'
toptime_key = 'video/top/time'
whiskertime_key = 'video/whisker/time'
leftpoke_key = 'task/poke/left/activity'
rightpoke_key = 'task/poke/right/activity'
rewards_key = 'task/rewards'
info_key = 'sessioninfo'

max_height_cm = 24.0
max_width_cm = 50.0
height_pixel_to_cm = max_height_cm / 680.0
width_pixel_to_cm = max_width_cm / 1280.0
rail_height_pixels = 100
rail_start_pixels = 200
rail_stop_pixels = 1000
frames_per_second = 120.0

h5filename = 'session.hdf5'
labelh5filename = 'labels.hdf5'
analysisfolder = 'Analysis'
backgroundfolder = 'Background'
playerpath = os.path.join(dname, r'../bonsai.lesions/Bonsai.Player.exe')
databasepath = 'C:/Users/Gon\xe7alo/kampff.lab@gmail.com/animals/'

def process_subjects(datafolders,preprocessing=True,overwrite=False):
    for basefolder in datafolders:
        datafolders = [path for path in directorytree(basefolder,1)
                       if os.path.isdir(path)]
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
        
    print "Generating datasets..."
    for i,path in enumerate(datafolders):
        print "Generating dataset for "+ path + "..."
        createdataset(i,path,overwrite=True)
        
def storepath(path):
    return os.path.join(path, analysisfolder, h5filename)
    
def labelpath(path):
    return os.path.join(path, analysisfolder, labelh5filename)

def readtimestamps(path):
    timestamps = pd.read_csv(path,header=None,names=['time'])
    return pd.to_datetime(timestamps['time'])
    
def scaletrajectories(ts,
          sx=width_pixel_to_cm,
          sy=height_pixel_to_cm,
          by=rail_height_pixels,
          my=max_height_cm):
    return [0,my,0,my] - (ts + [0,by,0,by]) * [-sx,sy,-sx,sy]
    
def sliceframe(slices):
    return pd.DataFrame([(s.start,s.stop) for s in slices],
                        columns=['start','stop'])
    
def indexseries(series,index):
    diff = len(index) - len(series)
    if diff > 0:
        msg="WARNING: time series length smaller than index by {0}. Padding..."
        print str.format(msg,diff)
        lastrow = series.tail(1)
        series = series.append([lastrow] * diff)
    series.index = index
    return series
    
def readdatabase(name):
    path = databasepath + name + '.csv'
    return pd.read_csv(path,
                       header=None,
                       names=['time','event','value'],
                       dtype={'time':pd.datetime,'event':str,'value':str},
                       parse_dates=[0],
                       index_col='time')
    
def readpoke(path):
    return pd.read_csv(path,
                       sep=' ',
                       header=None,
                       names=['activity','time'],
                       dtype={'activity':np.int32,'time':pd.datetime},
                       parse_dates=[1],
                       index_col=1,
                       usecols=[0,1])
                       
def readstep(path,name):
    return pd.read_csv(path,
                       header=None,
                       true_values=['True'],
                       false_values=['False'],
                       names=[name])[name]
        
def createdataset(session,path,overwrite=False):
    h5path = storepath(path)
    if os.path.exists(h5path):
        if overwrite:
            print "Overwriting..."
            os.remove(h5path)
        else:
            print "Skipped!"
            return

    # Load raw data
    fronttime = readtimestamps(os.path.join(path, 'front_video.csv'))
    toptime = readtimestamps(os.path.join(path, 'top_video.csv'))
    whiskertime = readtimestamps(os.path.join(path, 'whisker_video.csv'))
    leftrewards = readtimestamps(os.path.join(path, 'left_rewards.csv'))
    rightrewards = readtimestamps(os.path.join(path, 'right_rewards.csv'))
    leftpoke = readpoke(os.path.join(path, 'left_poke.csv'))
    rightpoke = readpoke(os.path.join(path, 'right_poke.csv'))
    
    # Load preprocessed data
    trajectorypath = os.path.join(path, analysisfolder, 'trajectories.csv')
    stepactivitypath = os.path.join(path, analysisfolder, 'step_activity.csv')
    gapactivitypath = os.path.join(path, analysisfolder, 'slip_activity.csv')
    trajectories = pd.read_csv(trajectorypath,
                               sep = ' ',
                               header=None,
                               dtype=np.int32,
                               names=['xhead','yhead','xtail','ytail'])
    stepactivity = pd.read_csv(stepactivitypath,
                               sep = ' ',
                               header = None,
                               dtype=np.int32,
                               names=[str.format('stepactivity{0}',i)
                               for i in xrange(8)])
    gapactivity = pd.read_csv(gapactivitypath,
                              sep = ' ',
                              header = None,
                              dtype=np.int32,
                              names=[str.format('gapactivity{0}',i)
                              for i in xrange(7)])
    trajectories = indexseries(trajectories,fronttime)
    scaledtrajectories = scaletrajectories(trajectories[trajectories >= 0])
    trajectories[trajectories < 0] = np.NaN
    trajectories[trajectories >= 0] = scaledtrajectories
    stepactivity = indexseries(stepactivity,fronttime)
    gapactivity = indexseries(gapactivity,fronttime)
    
    # Compute speed
    speed = trajectories.diff()
    timedelta = pd.DataFrame(fronttime.diff() / np.timedelta64(1,'s'))
    timedelta.index = speed.index
    speed = pd.concat([speed,timedelta],axis=1)
    speed = speed.div(speed.time,axis='index')    
    speed.columns = ['xhead_speed',
                     'yhead_speed',
                     'xtail_speed',
                     'ytail_speed',
                     'timedelta']
    speed['timedelta'] = timedelta
    
    # Compute reward times
    leftrewards = pd.DataFrame(leftrewards)
    rightrewards = pd.DataFrame(rightrewards)
    leftrewards['side'] = 'left'
    rightrewards['side'] = 'right'
    rewards = pd.concat([leftrewards,rightrewards])
    rewards.sort(columns=['time'],inplace=True)
    
    # Compute trial indices and environment state
    trialindex = pd.concat([fronttime[0:1],rewards.time])
    trialseries = pd.Series(range(len(trialindex)),
                            dtype=np.int32,
                            name='trial')
    if len(trialindex) > 200:
        print "WARNING: Trial count exceeded 200!"
    steppath = os.path.join(path, 'step{0}_trials.csv')
    axisname = 'stepstate{0}'
    stepstates = [readstep(str.format(steppath,i),str.format(axisname,i))
    for i in xrange(1,7)]
    trialseries = pd.concat([trialseries] + stepstates,axis=1)
    trialseries.fillna(method='ffill',inplace=True)
    trialseries = trialseries[0:len(trialindex)]
    trialseries.index = trialindex
    trialseries = trialseries.reindex(fronttime,method='ffill')
    
    # Generate session info
    starttime = fronttime[0].replace(second=0, microsecond=0)
    subjectfolder = os.path.split(path)[0]
    subject = os.path.split(subjectfolder)[1]
    protocol = sessionlabel(path)
    database = readdatabase(subject)
    weights = database[(database.event == 'Weight') &
                       (database.index < starttime)]
    weight = float(weights.ix[weights.index[-1]].value)
    cagemate = database[database.event == 'Housed'].ix[0].value
    lefthistology = database.event == 'Histology\LesionLeft'
    righthistology = database.event == 'Histology\LesionRight'
    lesionleft = float(database[lefthistology].value if lefthistology.any() else 0)
    lesionright = float(database[righthistology].value if righthistology.any() else 0)
    watertimes = database[(database.event == 'WaterDeprivation') &
                          (database.index < starttime)]
    if len(watertimes) > 0:
        deprivation = starttime - watertimes.index[-1]
    else:
        deprivation = 0
    info = pd.DataFrame([[subject,session,starttime,protocol,
                          weight,deprivation,lesionleft,lesionright,cagemate]],
                        columns=['subject',
                                 'session',
                                 'starttime',
                                 'protocol',
                                 'weight',
                                 'deprivation',
                                 'lesionleft',
                                 'lesionright',
                                 'cagemate'])
    info.set_index(['subject','session'],inplace=True)
    
    # Generate big data table
    frontactivity = pd.concat([trialseries,
                               trajectories,
                               speed,
                               stepactivity,
                               gapactivity],
                               axis=1)
    
    fronttime.to_hdf(h5path, fronttime_key)
    frontactivity.to_hdf(h5path, frontactivity_key)
    toptime.to_hdf(h5path, toptime_key)
    whiskertime.to_hdf(h5path, whiskertime_key)
    leftpoke.to_hdf(h5path, leftpoke_key)
    rightpoke.to_hdf(h5path, rightpoke_key)
    rewards.to_hdf(h5path, rewards_key)
    info.to_hdf(h5path, info_key)

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