# -*- coding: utf-8 -*-
"""
Created on Sat Aug 03 09:29:23 2013

@author: gonca_000
"""

import os
import load_data
import shuttling_analysis as sa

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
#editorpath = r'E:\Software\Bonsai.Packages\Externals\Bonsai\Bonsai.Editor\bin\x64\Release\Bonsai.Editor.exe'
editorpath = r'C:/Users/gonca_000/Documents/Insync/kampff.lab@gmail.com/protocols/shuttling/analysis/bonsai.lesions/Bonsai.Editor.exe'

def random_to_fully_released_transition_comparison():
    transitions = load_data.load_pathlist([
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_21/2013_04_26-11_53',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_22/2013_05_03-14_40',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_23/2013_05_03-13_38',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_24/2013_05_10-11_56',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_25/2013_05_10-12_31',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_27/2013_05_17-12_26',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_28/2013_05_24-12_22',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_29/2013_05_24-12_55',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_36/2013_07_26-13_46',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_26-14_21',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_38/2013_07_26-16_31',
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_39/2013_07_26-15_52'])
    sa.make_crossing_clips(transitions,frames_before=480,frames_after=480,labelfilter={'state':'released'},clipslice=slice(1))
    
def record_jump_jpak37():
    session = load_data.load_pathlist([
    r'D:/Protocols/Behavior/Shuttling/LightDarkServoStable/Data/JPAK_37/2013_07_26-14_21'])
    sa.make_crossing_clips(session,clipslice=slice(-14,-13))