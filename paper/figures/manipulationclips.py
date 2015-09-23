# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 20:09:02 2015

@author: Gonçalo
"""

import os
import pandas as pd
from activitymovies import getmovieframes, savemovie
from activitytables import info_key, read_sessions
from ethotables import manipulationtrials, shuffle
from datapath import lesionshamcache, visiblecrossings_key, sessionpath
from datapath import lesionshamanalysis

# Load data
info = pd.read_hdf(lesionshamcache, info_key)
info = info.query("protocol == 'stabletocenterfree'")
crossings = pd.read_hdf(lesionshamcache,visiblecrossings_key)
mtrials,fliptrials = manipulationtrials(crossings)

folders = sessionpath(info)
act = pd.concat([read_sessions(path,selector=lambda x:x.loc[time,:])
                 for path,time in zip(folders,mtrials.timeslice)])

# Save movies
dirname = os.path.join(lesionshamanalysis,'Movies')
if not os.path.exists(dirname):
    os.mkdir(dirname)

for (subject,session),sact in act.groupby(level=['subject','session']):
    sinfo = info.ix[[(subject,session)],:]
    frames = getmovieframes(sinfo,sact.frame)
    fname = str.format('manipulation_{0}.avi',shuffle.index(subject))
    tname = os.path.splitext(fname)[0] + '.csv'
    print str.format("Processing {0}...",fname)
    fname = os.path.join(dirname,fname)
    tname = os.path.join(dirname,tname)
    if os.path.exists(fname):
        continue
    savemovie(frames, fname, 120, flip=fliptrials.get(subject,None))
    sact.reset_index().time.to_csv(tname,index=False,
                                   date_format='%Y-%m-%dT%H:%M:%S.%f%z')
