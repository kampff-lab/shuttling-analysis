# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 18:27:17 2013

@author: gonca_000
"""

import os
import load_data
import video_player
import numpy as np
import process_trajectories as proctraj
import analysis_utilities as utils

### NOTE: TO ENCODE VIDEOS WITH FFMPEG USE
# ffmpeg -r 120 -i frame_name%04d.tif -q:v 0 video_name.avi

def generate_frame_clip(videofile,start,end,save=True):
    print start
    print end-start
    video_player.play_video_data(os.path.splitext(videofile)[0] + ".avi"," ",0,start,end,save=save)

def generate_crossing_clip(videofile,index,before=0,after=0,save=True):
    ts = np.genfromtxt(videofile,dtype=str)
    crossings = np.genfromtxt(os.path.split(videofile)[0] +'/Analysis/crossings.csv',dtype=str)
    align = np.nonzero(ts == crossings[index])[0][0]
    print align
    print (align+after)-(align-before)
    video_player.play_video_data(os.path.splitext(videofile)[0] + ".avi"," ",0,align-before,align+after,save=save)

def generate_ethogram_clip(videofile,before=239,after=360,save=True):
    ts = np.genfromtxt(videofile,dtype=str)
    etho = np.genfromtxt(os.path.split(videofile)[0] +'/Analysis/blind_ethogram.csv',dtype=str)
    if len(np.shape(etho)) == 1:
        etho = np.array([etho])
    align = np.nonzero(ts == etho[0][1])[0][0]
    print align
    print (align+after)-(align-before)
    video_player.play_video_data(os.path.splitext(videofile)[0] + ".avi"," ",0,align-before,align+after,save=save)
    
#### SUPP. MOVIE 1 ####    

#### FIRST CROSSING ####
#### CONTROL A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_03_31-18_46/front_video.csv'
generate_crossing_clip(videofile,0,519,840)

#### LESION A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_03_31-18_26/front_video.csv'
generate_crossing_clip(videofile,0,519,840)
########################

#### AFTER 2 CROSSINGS ####
#### CONTROL A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_03_31-18_46/front_video.csv'
generate_crossing_clip(videofile,2,359,480)

#### LESION A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_03_31-18_26/front_video.csv'
generate_crossing_clip(videofile,2,359,480)
#########################

#### SUPP. MOVIE 2 ####
before = 180
after = 180

fastest_stable = [] ## GENERATE FROM FIGURE 1 ALT SCRIPT
fastest_partial = [] ## GENERATE FROM FIGURE 1 ALT SCRIPT
fastest_unstable = [] ## GENERATE FROM FIGURE 1 ALT SCRIPT

### STABLE CONDITION ###
### CONTROL D ###
fastest_slice = fastest_stable[3]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_11-14_46/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+22,save=True)

### LESION D ###
fastest_slice = fastest_stable[10]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_11-15_20/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### CONTROL A ###
fastest_slice = fastest_stable[0]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_04-12_14/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### LESION A ###
fastest_slice = fastest_stable[7]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_04-11_40/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+4,save=True)

### PARTIALLY UNSTABLE CONDITION ###
### CONTROL E ###
fastest_slice = fastest_partial[4]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_18-12_39/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+39,save=True)

### LESION E ###
fastest_slice = fastest_partial[10]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_18-12_06/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### CONTROL F ###
fastest_slice = fastest_partial[5]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_09-14_37/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### LESION F ###
fastest_slice = fastest_partial[11]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_09-14_03/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+4,save=True)

### UNSTABLE CONDITION ###
### CONTROL B ###
fastest_slice = fastest_unstable[1]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_05_11-13_09/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+128,save=True)

### LESION B ###
fastest_slice = fastest_unstable[7]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_05_11-12_36/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### ENCORE CONTROL B ###
fastest_slice = fastest_unstable[1]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_05_11-13_09/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-int(before/5),fastest_slice.stop+int(after/2),save=True)

### ENCORE LESION B ###
fastest_slice = fastest_unstable[7]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_05_11-12_36/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-int(before/5),fastest_slice.stop+int(after/2),save=True)

### CONTROL C ###
fastest_slice = fastest_unstable[2]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_27-16_07/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after,save=True)

### LESION C ###
fastest_slice = fastest_unstable[8]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_27-16_41/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-before,fastest_slice.stop+after+0,save=True)

### ENCORE CONTROL C ###
fastest_slice = fastest_unstable[2]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_27-16_07/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-int(before/5),fastest_slice.stop+int(after/2),save=True)

### ENCORE LESION C ###
fastest_slice = fastest_unstable[8]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_27-16_41/front_video.csv'
generate_frame_clip(videofile,fastest_slice.start-int(before/5),fastest_slice.stop+int(after/2),save=True)

#### SUPP. MOVIE 3 ####

### EXPLORE (CONTROL D) ###
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_12-14_26/front_video.csv'
generate_ethogram_clip(videofile,after=1000)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"1x",scale);
#annotateRangeColor("normal",240,16,storagepath,2,"1x",scale);
#annotateRangeColor("explore",256,985,storagepath,3,"1x",scale);

### COMPENSATE (CONTROL G) ###
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/front_video.csv'
generate_ethogram_clip(videofile,after=120)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"1x",scale);
#annotateRangeColor("normal",240,39,storagepath,2,"1x",scale);
#annotateRangeColor("compensate",279,46,storagepath,3,"1x",scale);
#annotateRangeEmpty(325,36,storagepath,4,"1x",scale);

### ENCORE COMPENSATE (CONTROL G) ###
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/front_video.csv'
generate_ethogram_clip(videofile,before=129,after=120)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,129,storagepath,1,"0.2x",scale);
#annotateRangeColor("normal",130,39,storagepath,2,"0.2x",scale);
#annotateRangeColor("compensate",169,46,storagepath,3,"0.2x",scale);
#annotateRangeEmpty(215,36,storagepath,4,"0.2x",scale);

### HALT (LESION A) ###
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/front_video.csv';
generate_ethogram_clip(videofile,after=800)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"1x",scale);
#annotateRangeColor("normal",240,87,storagepath,2,"1x",scale);
#annotateRangeColor("halt",327,714,storagepath,3,"1x",scale);

### HALT (LESION F) ###
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_03-15_32/front_video.csv'
generate_ethogram_clip(videofile,after=1000)
## FIJI Parameters (SATURATED 2) ###

#### SUPP. MOVIE 4 ####

#### CONTROL A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_05-12_21/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,41,storagepath,2,"0.2x",scale);
#annotateRangeColor("compensate",281,30,storagepath,3,"0.2x",scale);
#annotateRangeColor("normal",311,53,storagepath,4,"0.2x",scale);
#annotateRangeEmpty(364,237-tailFrames,storagepath,5,"0.2x",scale);
#saveSeparator(240,72,startpath,scale);
#saveSeparator(600-tailFrames,722+72*5,endpath,scale);

#### CONTROL B ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_04_19-13_20/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,26,storagepath,2,"0.2x",scale);
#annotateRangeColor("compensate",266,27,storagepath,3,"0.2x",scale);
#annotateRangeColor("normal",293,79,storagepath,4,"0.2x",scale);
#annotateRangeEmpty(372,229-tailFrames,storagepath,5,"0.2x",scale);
#saveSeparator(240,72,startpath,scale);
#saveSeparator(600-tailFrames,722+72*5,endpath,scale);

#### CONTROL C ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_12-12_00/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,14,storagepath,2,"0.2x",scale);
#annotateRangeColor("compensate",254,51,storagepath,3,"0.2x",scale);
#annotateRangeEmpty(305,296-tailFrames,storagepath,4,"0.2x",scale);
#saveSeparator(240,72,startpath,scale);
#saveSeparator(600-tailFrames,722+72*5,endpath,scale);

#### CONTROL D ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_04_12-14_26/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,16,storagepath,2,"0.5x",scale);
#annotateRangeColor("explore",256,345,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,72*2,midpath,scale);
#saveSeparator(600,361+72*3,endpath,scale);

#### CONTROL E ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_12-11_16/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,24,storagepath,2,"0.5x",scale);
#annotateRangeColor("explore",264,337,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,72*2,midpath,scale);
#saveSeparator(600,361+72*3,endpath,scale);

#### CONTROL F ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_03-16_06/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters (SATURATED 2) ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,16,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",256,345,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### CONTROL G ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_04_26-13_52/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,39,storagepath,2,"0.2x",scale);
#annotateRangeColor("compensate",279,46,storagepath,3,"0.2x",scale);
#annotateRangeEmpty(325,276-tailFrames,storagepath,4,"0.2x",scale);
#saveSeparator(240,72,startpath,scale);
#saveSeparator(600-tailFrames,722+72*5,endpath,scale);

#### LESION A ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/front_video.csv';
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,87,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",327,274,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION B ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_04_19-12_45/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,16,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",256,345,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION C ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_12-12_33/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,69,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",309,213,storagepath,3,"0.5x",scale);
#annotateRangeColor("normal",522,24,storagepath,4,"0.5x",scale);
#annotateRangeEmpty(546,55,storagepath,5,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION D ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_04_12-14_59/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,49,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",289,128,storagepath,3,"0.5x",scale);
#annotateRangeColor("explore",417,184,storagepath,4,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION E ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_12-10_43/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,69,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",309,292,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION F ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_03-15_32/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters (SATURATED 2) ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,36,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",276,325,storagepath,3,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### LESION G ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_26/2013_04_26-14_25/front_video.csv'
generate_ethogram_clip(videofile)
## FIJI Annotation Parameters ###
#annotateRangeEmpty(1,239,storagepath,1,"0.5x",scale);
#annotateRangeColor("normal",240,35,storagepath,2,"0.5x",scale);
#annotateRangeColor("halt",275,56,storagepath,3,"0.5x",scale);
#annotateRangeColor("compensate",331,51,storagepath,4,"0.5x",scale);
#annotateRangeColor("halt",382,219,storagepath,5,"0.5x",scale);
#saveSeparator(240,361-tailFrames+72,startpath,scale);
#saveSeparator(240,361+72*4,midpath,scale);
#saveSeparator(600,72,endpath,scale);

#### ENRICHED CONTROLS 1-2 ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_42/2013_09_06-12_18/front_video.csv'
generate_ethogram_clip(videofile)

videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_43/2013_09_06-12_51/front_video.csv'
generate_ethogram_clip(videofile)

#### ENRICHED LESIONS 1-2 ####
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_40/2013_09_06-11_03/front_video.csv'
generate_ethogram_clip(videofile)

videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_41/2013_09_06-11_37/front_video.csv'
generate_ethogram_clip(videofile)

#### SUPP. MOVIE 5 ####
lesionAfolder = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20'
lesionAmanipsessions = load_data.load_path_trajectories(lesionAfolder,[5,6,7,8,9,10])
lesionAtrials = [proctraj.slice_trajectories(s) for s in lesionAmanipsessions]

offset = 2
leftmost_slices = [np.argmin([np.min(t[s,0]) for s in trials[offset:]])+offset for trials,t in zip(lesionAtrials,lesionAmanipsessions)]

#### LESION A FURTHEST TRIAL (MANIP+0) ####
attempt = lesionAtrials[0][24]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_05-11_47/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2500,save=True)

#### LESION A FURTHEST TRIAL (MANIP+1) ####
attempt = lesionAtrials[1][7]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_06-11_42/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2600,save=True)

#### LESION A FURTHEST TRIAL (MANIP+2) ####
attempt = lesionAtrials[2][34]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_08-11_38/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2400,save=True)
generate_frame_clip(videofile,attempt.start+2400,attempt.start+3000,save=True)
generate_frame_clip(videofile,attempt.start+3000,attempt.start+3600,save=True)
generate_frame_clip(videofile,attempt.start+3600,attempt.start+4200,save=True)

#### LESION A FURTHEST TRIAL (MANIP+3) ####
attempt = lesionAtrials[3][21]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_09-11_30/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2400,save=True)
generate_frame_clip(videofile,attempt.start+2400,attempt.start+3000,save=True)
generate_frame_clip(videofile,attempt.start+3000,attempt.start+3600,save=True)
generate_frame_clip(videofile,attempt.start+3600,attempt.start+4400,save=True)

#### LESION A FURTHEST TRIAL (MANIP+4) ####
attempt = lesionAtrials[4][2]
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_10-11_50/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2400,save=True)
generate_frame_clip(videofile,attempt.start+2400,attempt.start+3000,save=True)
generate_frame_clip(videofile,attempt.start+3000,attempt.start+3600,save=True)

#### LESION A FURTHEST TRIAL (MANIP+5) ####
attempt = lesionAtrials[5][8]
attempt = slice(attempt.start + 578,attempt.stop)
videofile = r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_20/2013_04_11-13_34/front_video.csv'
generate_frame_clip(videofile,attempt.start,attempt.start+600,save=True)
generate_frame_clip(videofile,attempt.start+600,attempt.start+1200,save=True)
generate_frame_clip(videofile,attempt.start+1200,attempt.start+1800,save=True)
generate_frame_clip(videofile,attempt.start+1800,attempt.start+2400,save=True)
generate_frame_clip(videofile,attempt.start+2400,attempt.start+3000,save=True)
generate_frame_clip(videofile,attempt.start+3000,attempt.start+3600,save=True)