# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 05:22:49 2014

@author: Gonçalo
"""

import os
import cv2
import video
import imgproc
import sessions
import datetime
import numpy as np
import pandas as pd
import activitymovies
import scipy.stats as stats
from scipy.interpolate import interp1d
from preprocess import appendtrialinfo
from preprocess import gapslice, stepslice
from preprocess import storepath, labelpath
from preprocess import frontactivity_key, rewards_key, info_key
from preprocess import leftpoke_key, rightpoke_key
from preprocess import max_width_cm, width_pixel_to_cm
from preprocess import rail_start_pixels, rail_stop_pixels
from preprocess import stepcenter_cm, slipcenter_cm
from preprocess import stepcenter_pixels, slipcenter_pixels
from preprocess import rail_start_cm, rail_stop_cm

def groupbyname(data,info):
    result = data.copy(True)
    result['l2'] = ['individual']*len(data)
    result.reset_index(inplace=True)
    result.sort(['session','subject'],inplace=True)
    result.set_index(['session','l2','subject'],inplace=True)
    return result

def groupbylesionvolumes(data,info):
    lesionvolume = info['lesionleft'] + info['lesionright']
    lesionvolume.name = 'lesionvolume'
    g = pd.concat([data,lesionvolume,info['cagemate']],axis=1)
    #joininfo = pd.concat((lesionvolume,info['cagemate']),axis=1)
    #g = data.join(joininfo)
    lesionorder = g[g['lesionvolume'] > 0].sort('lesionvolume',ascending=False)
    controls = lesionorder.groupby('cagemate',sort=False).median().index
    controls.name = 'subject' # OPTIONAL?
    controlorder = g.reset_index().set_index('subject').ix[controls]
    controlorder.set_index('session',append=True,inplace=True)
    
    result = pd.concat([controlorder,lesionorder])
    result['lesion'] = ['lesion' if v > 0 else 'control'
                        for v in result['lesionvolume']]
    result.reset_index(inplace=True)
    result = result[~result.session.isnull()]
    columns = ['subject' if c == 'level_0' else c for c in result.columns]
    result.columns = columns
    result.sort(['session','lesion'],inplace=True)
    result.set_index(['session','lesion','subject'],inplace=True)
    result.drop(['lesionvolume','cagemate'],axis=1,inplace=True)
    return result
    
def trialactivity(rr,lpoke,rpoke,cr,vcr):
    lpoketime = lpoke.groupby('trial').duration.sum().to_frame('poketime')
    rpoketime = rpoke.groupby('trial').duration.sum().to_frame('poketime')
    ptime = pd.concat([lpoketime,rpoketime]).sort()
    crtime = cr.groupby('trial').duration.sum().to_frame('crossingtime')
    vcrtime = vcr.groupby('trial').duration.sum()
    vtime = (vcrtime - crtime.crossingtime).to_frame('visibletime')
    ttime = rr.time.diff()[1:] / np.timedelta64(1,'s')
    ttime.columns = ['totaltime']
    trialact = pd.concat([ptime,vtime,crtime,ttime],
                         join='inner',axis=1)
    atime = trialact[['poketime','visibletime','crossingtime']].sum(axis=1)
    idletime = trialact.time - atime
    trialact.insert(3,'idletime',idletime)
    return trialact
    
def firstordefault(condition,default=None):
    indices = np.where(condition)[0]
    if len(indices) > 0:
        return condition.index[indices[0]]
    return default
    
def utcfromdatetime64(dt64):
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    return datetime.datetime.utcfromtimestamp(ts)
    
def getkeyloc(index,key):
    if np.iterable(key):
        return [index.get_loc(k) for k in key]
    return index.get_loc(key)

def geomediancost(median,xs):
    return np.linalg.norm(xs-median,axis=1).sum()
    
def mad(xs):
    median = xs.median()
    return (xs - median).abs().median()
    
def read_activity(path):
    return pd.read_hdf(storepath(path), frontactivity_key)
    
def read_rewards(path):
    return pd.read_hdf(storepath(path), rewards_key)
    
def read_crossings(path, activity):
    crosses = crossings(activity)
    labelh5path = labelpath(path)
    if os.path.exists(labelh5path):
        crosses.label = pd.read_hdf(labelh5path, 'label')
    return crosses
    
def read_crossings_group(folders):
    crossings = []
    for path in folders:
        activity = read_activity(path)
        cr = read_crossings(path, activity)
        cr['session'] = os.path.split(path)[1]
        crossings.append(cr)
    return pd.concat(crossings)
    
def appendlabels(data,labelspath):
    if os.path.exists(labelspath):
        with open(labelspath) as f:
            for line in f:
                label,value = line.split(':')
                try:
                    value = float(value)
                except ValueError:
                    value = value
                data[label] = value
    
def read_subjects(folders, days=None,
                  key=frontactivity_key, selector=None,includeinfokey=True):
    if isinstance(folders, str):
        folders = [folders]
                      
    subjects = []
    for path in folders:
        subject = read_sessions(sessions.findsessions(path, days),
                                key,selector,includeinfokey)
        subjects.append(subject)
    return pd.concat(subjects)
    
def read_sessions(folders, key=frontactivity_key, selector=None,
                  includeinfokey=True):
    if isinstance(folders, str):
        folders = [folders]
    
    multikey = not isinstance(key,str) & np.iterable(key)
    if multikey and selector is None:
        raise ValueError("A table selector has to be specified for multi-keys.")
    
    sessions = []
    for path in folders:
        if multikey:
            tables = [pd.read_hdf(storepath(path), k) for k in key]
            session = selector(*tables)
        else:
            session = pd.read_hdf(storepath(path), key)
            if selector is not None:
                session = selector(session)

        if key != info_key and includeinfokey:
            info = pd.read_hdf(storepath(path), info_key)
            info.reset_index(inplace=True)
            keys = [n for n in session.index.names if n is not None]
            session.reset_index(inplace=True)
            session['subject'] = info.subject.iloc[0]
            session['session'] = info.session.iloc[0]
            session.set_index(['subject', 'session'], inplace=True)
            session.set_index(keys, append=True, inplace=True)
        sessions.append(session)
    return pd.concat(sessions)
    
def read_canonical(folders,days=None):
    act = read_subjects(folders,days)
    cr = read_subjects(folders,days,selector=fullcrossings)
    fcr = read_subjects(folders,days,selector=crossings)
    info = read_subjects(folders,days,key=info_key)
    return act,cr,fcr,info
    
def slowdown(crossings):
    return pd.DataFrame(
    [stats.linregress(crossings.entryspeed,crossings.exitspeed)],
     columns=['slope','intercept','r-value','p-value','stderr'])
     
def findpeaks(ts,thresh,axis=-1):
    if isinstance(ts,pd.Series):
        ts = ts.to_frame()    
    
    valid = ts > thresh if thresh > 0 else ts < thresh
    masked = np.ma.masked_where(valid,ts)

    views = np.rollaxis(masked,axis) if ts.ndim > 1 else [masked]
    clumpedpeaks = []
    for i,view in enumerate(views):
        clumped = np.ma.clump_masked(view)
        peaks = [ts[slce].ix[:,i].argmax() if thresh > 0 else ts[slce].ix[:,i].argmin()
                 for slce in clumped]
        clumpedpeaks.append(peaks)
    return clumpedpeaks if len(clumpedpeaks) > 1 else clumpedpeaks[0]
     
def roiactivations(roiactivity,thresh,roicenters):
    roidiff = roiactivity.diff()
    roipeaks = findpeaks(roidiff,thresh)
    data = [(peak,i,roicenters[i][1],roicenters[i][0])
            for i,step in enumerate(roipeaks)
            for peak in step]
    data = np.array(data)
    data = data[np.argsort(data[:,0]),:]
    return data
     
def steptimes(activity,thresh=1500):
    stepactivity = activity.iloc[:,stepslice]
    data = roiactivations(stepactivity,thresh,stepcenter_cm)
    index = pd.Series(data[:,0],name='time')
    return pd.DataFrame(data[:,1:],
                        index=index,
                        columns=['stepindex',
                                 'stepcenterx',
                                 'stepcentery'])
                                 
def sliptimes(activity,thresh=1500):
    gapactivity = activity.iloc[:,gapslice]
    data = roiactivations(gapactivity,thresh,slipcenter_cm)
    index = pd.Series(data[:,0],name='time')
    return pd.DataFrame(data[:,1:],
                        index=index,
                        columns=['gapindex',
                                 'gapcenterx',
                                 'gapcentery'])

def spatialaverage(activity,crossings,selector=lambda x:x.yhead):
    ypoints = []
    xpoints = np.linspace(rail_start_cm,rail_stop_cm,100)
    for s,side in crossings[['timeslice','side']].values:
        trial = activity.xs(s,level='time')
        xhead = trial.xhead
        yhead = selector(trial)
        if side == 'leftwards':
            xhead = max_width_cm - xhead
        curve = interp1d(xhead,yhead,bounds_error=False)
        ypoints.append(curve(xpoints))
    ypoints = np.array(ypoints)
    return xpoints,np.mean(ypoints,axis=0),stats.sem(ypoints,axis=0)
    
#def stepframeindices(activity,crossings,leftstep,rightstep):
#    indices = []
#    side = []
#    for index,trial in crossings.iterrows():
#        leftwards = trial.side == 'leftwards'
#        stepindex = leftstep if leftwards else rightstep
#        stepactivity = activity.xs(trial.timeslice,level='time',
#                                   drop_level=False).iloc[:,stepslice]
#        stepdiff = stepactivity.diff()
#        steppeaks = findpeaks(stepdiff,1500)[stepindex]
#        steppeaks = [peak for peak in steppeaks
#                     if (activity.xhead[peak] > stepcenter_cm[rightstep] if leftwards else
#                         activity.xhead[peak] < stepcenter_cm[leftstep]).any()]
#        if len(steppeaks) > 0:
#            frameindex = min([activity.index.get_loc(peak) for peak in steppeaks])
#            indices.append(frameindex)
#            side.append(trial.side)
#    return indices,side

def getroipeaks(activity,roislice,trial,leftroi,rightroi,roicenters,
                usediff=True,thresh=1500,headinfront=True):
    leftwards = trial.side == 'leftwards'
    roiindex = leftroi if leftwards else rightroi
    roiactivity = activity.xs(trial.timeslice,level='time',
                              drop_level=False).ix[:,roislice]
    if usediff:
        roiactivity = roiactivity.diff()
    roipeaks = findpeaks(roiactivity,thresh)[roiindex]
    if headinfront:
        roipeaks = [peak for peak in roipeaks
                     if (activity.xhead[peak] > roicenters[rightroi] if leftwards else
                         activity.xhead[peak] < roicenters[leftroi]).any()]
    return roipeaks
    
def getsteppeaks(activity,trial,leftstep,rightstep):
    return getroipeaks(activity,slice(17,25),trial,leftstep,rightstep,stepcenter_cm)
    
def getslippeaks(activity,trial,leftgap,rightgap):
    return getroipeaks(activity,slice(25,32),trial,leftgap,rightgap,slipcenter_cm,
                       usediff=False,thresh=5000,headinfront=False)

def roicrossings(activity,crossings,leftroi,rightroi,getpeaks):
    indices = []
    
    for index,trial in crossings.iterrows():
        roipeaks = getpeaks(activity,trial,leftroi,rightroi)
        if len(roipeaks) > 0:
            indices.append(index)
    return crossings.loc[indices]

def stepcrossings(activity,crossings,leftstep,rightstep):
    return roicrossings(activity,crossings,leftstep,rightstep,getsteppeaks)
    
def slipcrossings(activity,crossings,leftgap,rightgap):
    return roicrossings(activity,crossings,leftgap,rightgap,getslippeaks)

def roiframeindices(activity,crossings,leftroi,rightroi,getpeaks):
    indices = []
    side = []
    
    for index,trial in crossings.iterrows():
        roipeaks = getpeaks(activity,trial,leftroi,rightroi)            
        if len(roipeaks) > 0:
            frameindex = min([activity.index.get_loc(peak) for peak in roipeaks])
            indices.append(frameindex)
            side.append(trial.side)
    return indices,side
    
def stepframeindices(activity,crossings,leftstep,rightstep):
    return roiframeindices(activity,crossings,leftstep,rightstep,getsteppeaks)
    
def slipframeindices(activity,crossings,leftgap,rightgap):
    return roiframeindices(activity,crossings,leftgap,rightgap,getslippeaks)
    
def stepfeature(activity,crossings,leftstep,rightstep):
    indices,side = stepframeindices(activity,crossings,leftstep,rightstep)
    features = activity.ix[indices,:]
    features['side'] = side
    return features
#    side = pd.DataFrame(side,columns=['side'])
#    side.index = features.index
#    return pd.concat((features,side),axis=1)

def croproi(frame,roiindex,roicenter_pixels,cropsize=(300,300),background=None,
            flip=False,cropoffset=(0,0)):
    roicenter = roicenter_pixels[roiindex]
    roicenter = (roicenter[0] + cropoffset[0], roicenter[1] + cropoffset[1])
    
    frame = imgproc.croprect(roicenter,cropsize,frame)
    if background is not None:
        background = imgproc.croprect(roicenter,cropsize,background)
        frame = cv2.subtract(frame,background)
    if flip:
        frame = cv2.flip(frame,1)
    return frame
    
def cropstep(frame,stepindex,cropsize=(300,300),background=None,flip=False):
    return croproi(frame,stepindex,stepcenter_pixels,cropsize,background,flip)
    
def cropslip(frame,gapindex,cropsize=(300,300),background=None,flip=False):
    return croproi(frame,gapindex,slipcenter_pixels,cropsize,background,flip,
                   cropoffset=(-100,0))

def roiframes(indices,side,info,leftroi,rightroi,croproi,
               cropsize=(300,300),subtractBackground=False):
    # Tile step frames    
    vidpaths = activitymovies.getmoviepath(info)
    timepaths = activitymovies.gettimepath(info)
    backpaths = activitymovies.getbackgroundpath(info)
    videos = [video.video(path,timepath) for path,timepath in zip(vidpaths,timepaths)]
    
    frames = []
    for frameindex,side in zip(indices,side):
        leftwards = side == 'leftwards'
        roiindex = leftroi if leftwards else rightroi
        
        frame = videos[0].frame(frameindex)
        background = None
        if subtractBackground:
            timestamp = videos[0].timestamps[frameindex]
            background = activitymovies.getbackground(backpaths[0],timestamp)
        frame = croproi(frame,roiindex,cropsize,background,roiindex == rightroi)
        frames.append(frame)
    return frames
    
def stepframes(activity,crossings,info,leftstep,rightstep,
               cropsize=(300,300),subtractBackground=False):
    indices,side = stepframeindices(activity,crossings,leftstep,rightstep)
    return roiframes(indices,side,info,leftstep,rightstep,
                     cropstep,cropsize,subtractBackground)
                     
#def slipframes(activity,crossings,info,leftgap,rightgap,
#               cropsize=(300,300),subtractBackground=False):
#    indices,side = slipframeindices(activity,crossings,leftgap,rightgap)
#    return roiframes(indices,side,info,leftgap,rightgap,
#                     cropslip,cropsize,subtractBackground)
                     
def slipactivity(activity):
    rowindex = []
    rows = []    
    
    roiactivity = activity.ix[:,25:32]
    roipeaks = findpeaks(roiactivity,5000)
    for gapindex,gap in enumerate(roipeaks):
        for slip in gap:
            gapcenter = slipcenter_cm[gapindex]
            slipactivity = roiactivity.ix[slip,gapindex]
            rowindex.append(slip)
            rows.append((gapindex,gapcenter[0],gapcenter[1],slipactivity))
    rowindex = pd.MultiIndex.from_tuples(rowindex,names=activity.index.names)
    data = pd.DataFrame(rows,rowindex,
                        columns=['gapindex','xgap','ygap','peakactivity'])
    return data

#def slipactivity(activity,crossings):
#    rowindex = []
#    rows = []
#    
#    for index,trial in crossings.iterrows():
#        roiactivity = activity.xs(trial.timeslice,level='time',
#                                  drop_level=False).ix[:,25:32]
#        roipeaks = findpeaks(roiactivity,5000)
#        for gapindex,gap in enumerate(roipeaks):
#            for slip in gap:
#                gapcenter = slipcenter_cm[gapindex]
#                slipactivity = roiactivity.ix[slip,gapindex]
#                rowindex.append(slip)
#                rows.append((gapindex,gapcenter[0],gapcenter[1],
#                             slipactivity,trial.side))
#    indexnames = crossings.index.names + ['time']
#    rowindex = pd.MultiIndex.from_tuples(rowindex,names=indexnames)
#    data = pd.DataFrame(rows,rowindex,
#                        columns=['gapindex','xgap','ygap',
#                                 'peakactivity','side'])
#    return data.join(activity)
    
def countslipevents(slipactivity):
    slipactivity = slipactivity.reset_index()
    return slipactivity.groupby(['subject','session',
                                 'trial','gapindex'])['gapindex'].count()
    
def coldist(xs,xcol1,xcol2,ycol1,ycol2):
    return np.sqrt((xs[xcol1]-xs[xcol2])**2 + (xs[ycol1]-xs[ycol2])**2)
    
def setlist(l,mask,val):
    for i,v in enumerate(mask):
        if v:
            l[i] = val
    
def slipfilter(slipactivity):
    criteria = True
    gapcriteria = (slipactivity.gapindex > 0) & (slipactivity.side == 'rightwards')
    gapcriteria |= (slipactivity.gapindex < 6) & (slipactivity.side == 'leftwards')
#    criteria &= gapcriteria
    criteria &= slipactivity.yhead < 15
    criteria &= slipactivity.peakactivity > 8000
    criteria &= abs(slipactivity.xtail-slipactivity.xgap) > 5
    criteria &= (slipactivity.gapindex > 0) & (slipactivity.gapindex < 6)
    return criteria
    
def slipframes(slipactivity,info,cropsize=(300,200),
               subtractBackground=False):
    vidpaths = activitymovies.getmoviepath(info)
    timepaths = activitymovies.gettimepath(info)
    backpaths = activitymovies.getbackgroundpath(info)
    videos = [video.video(path,timepath) for path,timepath in zip(vidpaths,timepaths)]

    frames = []    
    for index,trial in slipactivity.iterrows():
        rightwards = trial.side == 'rightwards'
        frame = videos[0].frame(trial.frame)
        background = None
        if subtractBackground:
            timestamp = videos[0].timestamps[trial.frame]
            background = activitymovies.getbackground(backpaths[0],timestamp)
        if cropsize is not None:
            frame = cropslip(frame,trial.gapindex,cropsize,background,rightwards)
        frames.append(frame)
    return frames
    
def __lickbouts__(licks,time):
    bouts = []
    lickcounts = []
    for i,s in enumerate(licks):
        if len(bouts) == 0:
            bouts.append(s)
            lickcounts.append(1)
        else:
            currbout = bouts[-1]
            ili = time[s.start] - time[currbout.stop]
            if ili > datetime.timedelta(seconds=1.5):
                bouts.append(s)
                lickcounts.append(1)
            else:
                bouts[-1] = slice(currbout.stop,s.stop)
                lickcounts[-1] += 1
    return bouts,lickcounts
    
__mem__ = None    
    
def pokebouts(poke,rr):
#    baseline = poke.median()
#    thresh = baseline + poke.std()
    thresh = 400 # from actual threshold values
    masked = np.ma.masked_array(poke, poke > thresh)
    flat = np.ma.clump_unmasked(masked)
    licks = [slice(flat[i-1].stop-1,flat[i].start)
            for i in range(1,len(flat))]
    
    # Generate poke features
    time = poke.index
    bouts,lickcounts = __lickbouts__(licks,time)
    if len(bouts) == 0:
        return pd.DataFrame()
    trialinfo = appendtrialinfo(poke.reset_index('time').time,rr,[rr])
    if len(rr) == 0:
        rewardoffset = [1] * len(bouts)
    else:
        rewardoffset = [abs((time[s.stop-1]-trialinfo.time[s.stop-1]).total_seconds())
                       for s in bouts]
    trialinfo = pd.DataFrame([trialinfo.trial[s].max() + (1 if o < 1 else 0)
                             for o,s in zip(rewardoffset,bouts)],
                             columns=['trial'])
    timeslice = pd.DataFrame([slice(time[s.start],time[s.stop-1])
                             for s in bouts],columns=['timeslice'])
    duration = pd.DataFrame([(time[s.stop-1]-time[s.start]).total_seconds()
                            for s in bouts],
                            columns=['duration'])
    peak = pd.DataFrame([poke[s].max()[0] for s in bouts],columns=['peak'])
    bouts = pd.DataFrame(bouts,columns=['slices'])
    licks = pd.DataFrame(lickcounts,columns=['licks'])
    return pd.concat([bouts,
                      timeslice,
                      trialinfo,
                      duration,
                      licks,
                      peak],
                      axis=1)

def cropcrossings(x,slices,crop):
    def test_slice(s):
        return (x[s] > crop[0]) & (x[s] < crop[1])
    
    def crop_slice(s):
        valid_indices = np.nonzero(test_slice(s))[0]
        min_index = np.min(valid_indices)
        max_index = np.max(valid_indices)
        return slice(s.start+min_index,s.start+max_index+1)
    return [crop_slice(s) for s in slices if np.any(test_slice(s))]

def visiblecrossings(activity):
    return fullcrossings(activity,midcross=False)

def fullcrossings(activity,midcross=True):
    return crossings(activity,midcross,False)

def crossings(activity,midcross=True,crop=True,center=max_width_cm / 2.0):
    # Generate trajectories and crossings
    cropleft = rail_start_pixels * width_pixel_to_cm
    cropright = rail_stop_pixels * width_pixel_to_cm
    xhead = activity.xhead
    crossings = np.ma.clump_unmasked(np.ma.masked_invalid(activity.xhead))
    if midcross:
        crossings = [s for s in crossings
        if xhead[s.start] > center and xhead[s.stop-1] < center
        or xhead[s.start] < center and xhead[s.stop-1] > center]
    if crop:
        crossings = cropcrossings(xhead,crossings,[cropleft,cropright])
        
    if len(crossings) == 0:
        return pd.DataFrame()
        
    # Trial info
    trialinfo = pd.DataFrame([activity.iloc[s.start,1:8] for s in crossings])
    trialinfo.reset_index(inplace=True,drop=True)
    trialinfo['stepstate'] = np.bitwise_or(1 << 7, np.bitwise_or(
        np.left_shift(trialinfo['stepstate1'], 6), np.bitwise_or(
        np.left_shift(trialinfo['stepstate2'], 5), np.bitwise_or(
        np.left_shift(trialinfo['stepstate3'], 4), np.bitwise_or(
        np.left_shift(trialinfo['stepstate4'], 3), np.bitwise_or(
        np.left_shift(trialinfo['stepstate5'], 2), np.bitwise_or(
        np.left_shift(trialinfo['stepstate6'], 1), 1)))))))
    
    # Generate crossing features
    time = activity.index
    timeslice = pd.DataFrame([slice(time[s.start],time[s.stop-1])
                             for s in crossings],columns=['timeslice'])
    label = pd.DataFrame(['valid' for s in crossings],columns=['label'])
    position = pd.DataFrame([(activity.xhead[s].min(),activity.xhead[s].max())
                            for s in crossings],
                            columns=['xhead_min','xhead_max'])
    height = pd.DataFrame([activity.yhead[s].describe() for s in crossings])
    height.columns = 'yhead_' + height.columns
    height.columns = [c.replace('%','') for c in height.columns]
    speed = pd.DataFrame([activity.xhead_speed[s].abs().describe()
                         for s in crossings])
    speed.columns = 'xhead_speed_' + speed.columns
    speed.columns = [c.replace('%','') for c in speed.columns]
    duration = pd.DataFrame([(time[s.stop-1]-time[s.start]).total_seconds()
                            for s in crossings],
                            columns=['duration'])
    side = pd.DataFrame(['rightwards' if activity.xhead[s.start] < center else 'leftwards'
                        for s in crossings], columns=['side'])
    crosstime = pd.DataFrame([firstordefault(activity.xhead[s] >= center)
                             if activity.xhead[s.start] < center
                             else firstordefault(activity.xhead[s] <= center)
                             for s in crossings], columns=['crosstime'])
    
    # Slowdown
    xspeed = activity.xhead_speed
    entrydistance = (cropright - cropleft) / 3.0    
    entrypoints = [xhead[s] < (cropleft + entrydistance)
    if xhead[s.stop-1] > xhead[s.start]
    else xhead[s] > (cropright - entrydistance)
    for s in crossings]
    exitpoints = [xhead[s] > (cropright - entrydistance)
    if xhead[s.stop-1] > xhead[s.start]
    else xhead[s] < (cropleft + entrydistance)
    for s in crossings]
        
    entryspeed = pd.DataFrame([np.abs(xspeed[s][v].mean())
    for s,v in zip(crossings,entrypoints)],columns=['entryspeed'])
    crossingspeed = pd.DataFrame([np.abs(xspeed[s][~v & ~x].mean())
    for s,v,x in zip(crossings,entrypoints,exitpoints)],
    columns=['crossingspeed'])    
    exitspeed = pd.DataFrame([np.abs(xspeed[s][v].mean())
    for s,v in zip(crossings,exitpoints)],columns=['exitspeed'])
        
    # Steps
    steptimes = pd.DataFrame([[step[0] if len(step) > 0 else None
                 for step in findpeaks(activity.ix[s,stepslice].diff(),1500)]
                 for s in crossings])
    steptimes.columns = [str.format('steptime{0}',i)
                         for i in xrange(len(steptimes.columns))]
    
    # Slips
    gapactivity = pd.DataFrame([activity.ix[s,gapslice].max() for s in crossings])
    gapactivity.columns = [str.format('maxgap{0}',i)
                          for i in xrange(len(gapactivity.columns))]
    
    crossings = pd.DataFrame(crossings,columns=['slices'])
    return pd.concat([crossings,
                      timeslice,
                      label,
                      trialinfo,
                      duration,
                      position,
                      height,
                      speed,
                      side,
                      crosstime,
                      steptimes,
                      entryspeed,
                      crossingspeed,
                      exitspeed,
                      gapactivity],
                      axis=1)
    