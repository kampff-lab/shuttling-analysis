# -*- coding: utf-8 -*-
"""
Created on Sun Sep 02 16:56:25 2012

@author: IntelligentSystems
"""

import os
import glob
import shutil
import filecmp
import subprocess
import analysis_utilities as utils
import parse_session as parser
import process_session
import numpy as np
import matplotlib as mpl
import process_trajectories as proctraj

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
# old bonsai
#    playerpath = dname + r'\bonsai\Bonsai.Player.exe'
# current bonsai
analysisfolder = 'Analysis'
backgroundfolder = 'Background'
#playerpath = r'E:\Software\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Player.exe'
editorpath = r'D:\Bonsai\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Editor.exe'
playerpath = r'D:\Bonsai\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Player.exe'

def subject_analysis(datafolders,preprocessing=False):
    for basefolder in datafolders:
        datafolders = [path for path in utils.directory_tree(basefolder,1)]
        analysis_pipeline(datafolders,preprocessing=preprocessing)

def analysis_pipeline(datafolders,preprocessing=True):
    
    if preprocessing:
        print 'Generating labels...'
        make_lesionsham_session_label(datafolders)
        
        for path in datafolders:
            # Check for front activity file and regenerate if necessary
            front_activity_path = os.path.join(path,'front_activity.csv')
            if not os.path.exists(front_activity_path):
                analysispath = os.path.join(path,analysisfolder)
                os.chdir(analysispath)
                print 'Generating front activity data...'
                activitydetector = os.path.join(dname,'video_activity_detector.bonsai')
                subprocess.call([playerpath,activitydetector])
            
        for path in datafolders:
            print "Pre-processing "+ path + "..."
            print "Generating crossings..."
            newcrossings = make_crossings(path)
            analysispath = os.path.join(path,analysisfolder)
            currdir = os.getcwd()
            os.chdir(analysispath)
            
            # Filter crossings
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
    
def get_lesionsham_session_label(path):
    protocolfilefolder = os.path.join(dname,'protocolfiles/lesionsham')
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
    
def make_lesionsham_session_label(datafolders):
    for path in datafolders:
        label = get_lesionsham_session_label(path)
        session_labels_file = os.path.join(path,'session_labels.csv')
        if not os.path.exists(session_labels_file):
            np.savetxt(session_labels_file,[['protocol',label]],delimiter=':',fmt='%s')

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
    if len(cross_in) > 0:
        valid_crosses = np.insert(ici > 120,0,True)
    else:
        valid_crosses = np.array([],dtype=bool)
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
    
def update_clipdirectories(workingdirs,currdir):
    global dname
    os.chdir(dname)
    with open('clipDirectories.csv','w') as f:
        for dirname in workingdirs:
            f.write(dirname + '\n')
    os.chdir(currdir)
    
def write_time_slices(filename,time_slices):
    def write_crossing_slice(f,slices):
        for time_slice in slices:
            f.write('%s WindowOpening\n' % (time_slice[0]))
            f.write('%s WindowClosing\n' % (time_slice[1]))
    
    with open(filename,'w') as f:
        write_crossing_slice(f,time_slices)
    
def make_clips(session,labelfilter=None,slicesel=None,filename='player.csv'):
    currdir = os.getcwd()
    analysis_path = proctraj.get_analysis_path(session.video)
    if slicesel is None:
        indices = proctraj.get_labeled_indices(session.labels,labelfilter)
        time_slices = [(session.time[session.slices[i].start], session.time[session.slices[i].stop-1]) for i in indices]
    else:
        time_slices = [(session.time[s.start], session.time[s.stop-1]) for s in slicesel]
    
    os.chdir(analysis_path)
    write_time_slices(filename,time_slices)
    os.chdir(currdir)
    return analysis_path
    
def make_crossing_clips(sessions,frames_before=240,frames_after=240,xboundary=640,labelfilter=None,clipslice=slice(None),filename='player.csv'):
    currdir = os.getcwd()
    workingdirs = []
    for session in sessions:
        os.chdir(session.path[0])
        workingdirs.append(session.path[0])
        
        def write_crossing_slice(f,slices):
            for time_slice in slices:
                f.write('%s WindowOpening\n' % (time_slice[0]))
                f.write('%s WindowClosing\n' % (time_slice[1]))
        
        if labelfilter is not None:
            trials_filter = process_session.get_crossing_label_filter(session,labelfilter)
        else:
            trials_filter = lambda i:True
        time_slices = process_session.get_crossing_time_slices(session,frames_before,frames_after,xboundary,trialfilter=trials_filter,crossingslice=clipslice)
        
        with open(filename,'w') as f:
            write_crossing_slice(f,time_slices)
    
    update_clipdirectories(workingdirs,currdir)
    
def reconstruct_rewards(path,lthreshold=400,rthreshold=400):
    currdir = os.getcwd()
    os.chdir(path)
    
    left_activity = np.genfromtxt(r'left_poke.csv',usecols=0)
    left_times = np.genfromtxt(r'left_poke.csv',usecols=1,dtype=str)
    right_activity = np.genfromtxt(r'right_poke.csv',usecols=0)
    right_times = np.genfromtxt(r'right_poke.csv',usecols=1,dtype=str)
    
    left_activations = (left_activity > lthreshold).nonzero()[0]
    right_activations = (right_activity > rthreshold).nonzero()[0]
    
    def get_next_reward(activations,times,index,last_reward_time):
        for i in range(index,len(activations)):
            if times[activations[i]] > last_reward_time:
                return i
        return None

    left_index = 0
    right_index = 0
    left_rewards = []
    right_rewards = []
    left_reward = True
    last_reward_time = None
    while True:
        if left_reward:
            reward_index = get_next_reward(left_activations,left_times,left_index,last_reward_time)
            if reward_index is None:
                break
            reward = left_times[left_activations[reward_index]]
            left_rewards.append(reward)
            left_index = reward_index
        else:
            reward_index = get_next_reward(right_activations,right_times,right_index,last_reward_time)
            if reward_index is None:
                break
            reward = right_times[right_activations[reward_index]]
            right_rewards.append(reward)
            right_index = reward_index
        
        last_reward_time = reward
        left_reward = not left_reward
    
    np.savetxt('left_rewards.csv',left_rewards,'%s')
    np.savetxt('right_rewards.csv',right_rewards,'%s')
    
    os.chdir(currdir)

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

def shuttling_analysis(path):
    if not os.path.exists(path):
        return
    
    global dname
    currdir = os.getcwd()
    print "Processing "+ path + "..."
    os.chdir(path)
    
#    delete_video_analysis()
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

#    if not os.path.exists('trajectories.csv'):
#        videoprocessing = dname + r'\nose_tracker.bonsai'
#        print "Analysing tip trajectories..."
#        subprocess.call([playerpath, videoprocessing])
#        
#    if not os.path.exists('slip_activity.csv'):
#        videoprocessing = dname + r'\slip_tracker.bonsai'
#        print "Analysing slip activity..."
#        subprocess.call([playerpath, videoprocessing])
#        
#    if not os.path.exists('trajectory_steps.csv'):
#        videoprocessing = dname + r'\step_activity_tracker.bonsai'
#        print "Analysing step activities..."
#        subprocess.call([playerpath, videoprocessing])

#    stepfile = 'step0_times.csv'
#    if not os.path.exists(stepfile) or os.stat(stepfile).st_size == 0 or True:
#        print "Extracting step times..."
#        session = parser.parse_session(path,path,True)
#        process_session.make_step_times(session)
#        print "Saving step frames..."
#        buildsteppath = dname + r'\stepper_steps\build_step_frames'
#        os.system(buildsteppath)
#        print "Saving average step frames..."
#        process_session.make_step_means(session)

    os.chdir(currdir)