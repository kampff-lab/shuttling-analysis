# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 02:03:26 2014

@author: gonca_000
"""

import subprocess
ffmpeg_path = r'C:/Users/gonca_000/Documents/Software/ffmpeg/ffmpeg.exe'

def video_timepoint(index,fps):
    total_seconds = index / fps
    total_minutes = total_seconds / 60
    
    hours = total_minutes / 60
    minutes = total_minutes % 60
    seconds = total_seconds % 60
    fraction = (index % fps) * 1000 / fps
    return hours,minutes,seconds,fraction
    
def ffmpeg_timepoint(timepoint):
    return str.format('{0:02d}:{1:02d}:{2:02d}.{3:03d}',
                      timepoint[0],timepoint[1],timepoint[2],timepoint[3])

def slice_video(filename,start,end,fps,output):
    offset = video_timepoint(start,fps)
    duration = video_timepoint(end-start,fps)
    ss = ffmpeg_timepoint(offset)
    t = ffmpeg_timepoint(duration)
    subprocess.call([ffmpeg_path,'-y',
                     '-ss',ss,
                     '-t',t,
                     '-i',filename,
                     '-vf','extractplanes=y',
                     '-vb','20M',
                     '-vcodec','mpeg4',
                     output])
                     
def slice_trials(filename,trials,fps,output):
    for i,trial in enumerate(trials):
        out = str.format('{0}{1}.avi',output,i)
        slice_video(filename,trial[0],trial[1],fps,out)
        
def mux_multiple(videos,audios,output):
    for i,(v,a) in enumerate(zip(videos,audios)):
        out = str.format('{0}{1}.avi',output,i)
        mux_raw_audio(v,a,out)
        
def mux_raw_audio(video,audio,output):
    subprocess.call([ffmpeg_path,'-y',
                     '-f','s16le',
                     '-ar','48000',
                     '-ac','1',
                     '-i',audio,
                     '-i',video,
                     '-vb','20M',
                     '-vcodec','mpeg4',
                     output])