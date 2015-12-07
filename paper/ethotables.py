# -*- coding: utf-8 -*-
"""
Created on Tue Aug 04 15:24:13 2015

@author: Gonçalo
"""

import os
import ethogram
import pandas as pd

annotationpath = os.path.join(os.path.dirname(__file__),'annotations')
shuffle = ['JPAK_49', 'JPAK_28', 'JPAK_23', 'JPAK_50', 'JPAK_38', 'JPAK_37',
           'JPAK_25', 'JPAK_21', 'JPAK_51', 'JPAK_52', 'JPAK_48', 'JPAK_53',
           'JPAK_54', 'JPAK_27', 'JPAK_29', 'JPAK_20', 'JPAK_22', 'JPAK_26',
           'JPAK_55', 'JPAK_36', 'JPAK_39', 'JPAK_24']
           
def read_annotations():
    frames = []
    filenames = os.listdir(annotationpath)
    filenames = ((int(name.split('_',2)[1]),name) for name in filenames
                 if os.path.isfile(os.path.join(annotationpath, name)))
    filenames = sorted(filenames,key=lambda x:x[0])
    for i,name in filenames:
        subject = shuffle[i]
        fname = os.path.join(annotationpath,name)
        events = ethogram.load_events(fname)
        etime = [evt.timestamp for evt in events]
        ename = [evt.name for evt in events]
        etype = [evt.type for evt in events]
        esubject = [subject for evt in events]
        esession = [5 for evt in events]
        data = {'subject':esubject,'session':esession,'time':etime,
                'name':ename,'type':etype}
        frame = pd.DataFrame(data)
        frame.set_index(['subject','session','time'],inplace=True)
        frames.append((subject,frame))
    frames = (x[1] for x in sorted(frames,key=lambda x:x[0]))
    return pd.concat(frames)

def manipulationtrials(crossings):
    mtrials = crossings.query('session == 5 and trial >= 20')

    # Remove manipulation trials where rat jumped over
    mtrials = mtrials.query("subject != 'JPAK_50' or index > 34")
    mtrials = mtrials.query("subject != 'JPAK_52' or index > 24")
    fliptrials = {'JPAK_50':1,'JPAK_52':1}
    
    # Select first contact trials
    mtrials = mtrials[mtrials.crosstime.notnull()]
    mtrials.reset_index(inplace=True)
    mtrials = mtrials.drop_duplicates(subset=['subject','session'])
    mtrials.set_index(['subject','session'],inplace=True)
    return mtrials, fliptrials