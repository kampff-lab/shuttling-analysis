# -*- coding: utf-8 -*-
"""
Created on Sat Jun 08 18:54:22 2013

@author: gonca_000
"""

import subprocess

def play_video(path,playbackrate=0,startframe=0,endframe=None):
    videoplayerpath = r'G:/Bonsai/Bonsai.VideoPlayer/Bonsai.VideoPlayer/bin/x64/Release/Bonsai.VideoPlayer.exe'
    args = [videoplayerpath,path,str(playbackrate),str(startframe)]
    if endframe is not None:
        args.append(str(endframe))
    subprocess.Popen(args)

def play_video_data(path,datapath,playbackrate=0,startframe=0,endframe=None,save=False):
    videoplayerpath = r'D:/Bonsai/Bonsai.DataPlayer/Bonsai.VideoPlayer/bin/x64/Release/Bonsai.VideoPlayer.exe'
    args = [videoplayerpath,path,datapath,str(playbackrate),str(startframe)]
    if endframe is not None:
        args.append(str(endframe))
    if save:
        args.append('--save')
    subprocess.Popen(args)