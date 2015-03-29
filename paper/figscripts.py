# -*- coding: utf-8 -*-
"""
Created on Sun Nov 02 11:09:42 2014

@author: Gonçalo
"""

import itertools
def compress(data, selectors):
    # compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
    return (d for d, s in itertools.izip(data, selectors) if s)

import os
import figure1
import activitytables
import pandas as pd
import numpy as np

gioias = [r'D:/Protocols/Shuttling/Decorticate/Data/GIOIA_01',
          r'D:/Protocols/Shuttling/Decorticate/Data/GIOIA_03']

subjects = [r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_20',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_21',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_22',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_23',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_24',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_25',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_26',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_27',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_28',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_29',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_36',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_37',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_38',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_39',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_48',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_49',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_50',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_51',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_52',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_53',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_54',
            r'D:/Protocols/Shuttling/LightDarkServoStable/Data/JPAK_55']
            
decorticates = [r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_79',
                r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_81',
                r'D:/Protocols/Shuttling/Decorticate/Data/JPAK_82']
                
subjects = gioias+subjects+decorticates

cr = activitytables.read_subjects(subjects[1:],days=[3,4,9,10,-1],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,9,10,-1],
                                    key=activitytables.info_key)

# Figure 1B (Across Conditions)
rr = activitytables.read_subjects(subjects,days=range(1,5),
                                  key=activitytables.rewards_key)
info = activitytables.read_subjects(subjects,days=range(1,5),
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1b'
figure1.figure1b(rr,info,fbase)

# Figure 1B (Across All Conditions)
rr = activitytables.read_subjects(subjects,days=None,
                                  key=activitytables.rewards_key)
info = activitytables.read_subjects(subjects,days=None,
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1b\all'
figure1.figure1b(rr,info,fbase)

# Figure 1B2 (Trial Activity)
info = activitytables.read_subjects(subjects,days=None,
                                    key=activitytables.info_key)
stable = info.query('session > 0 and session < 5')
manipulation = info.query('session == 5')
sinfo = stable
lesionmask = (sinfo.lesionleft+sinfo.lesionright) > 0
biglesionmask = (sinfo.lesionleft + sinfo.lesionright) > 15
fbase = r'C:\figs\figure1b2'
figure1.figure1b2(stable,fbase,'stable')
figure1.figure1b2(manipulation,fbase,'manipulation')

figure1.figure1b2(sinfo[~lesionmask],fbase,'controls_stable')
figure1.figure1b2(sinfo[lesionmask],fbase,'lesions_stable')
figure1.figure1b2(sinfo[biglesionmask],fbase,'biglesions_stable')

sinfo = manipulation
lesionmask = (sinfo.lesionleft+sinfo.lesionright) > 0
biglesionmask = (sinfo.lesionleft + sinfo.lesionright) > 15

figure1.figure1b2(sinfo[~lesionmask],fbase,'controls_manipulation')
figure1.figure1b2(sinfo[lesionmask],fbase,'lesions_manipulation')
figure1.figure1b2(sinfo[biglesionmask],fbase,'biglesions_manipulation')

                                    
# Figure 1C (Across Conditions)
alpha=1
fbase = r'C:\figs\figure1c'
scr = cr.query('session != 3 and session != 9')
sinfo = info.query('session != 3 and session != 9')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_0.png')
figure1.figure1c2(scr,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_0a_colored.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_1_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_2_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_3_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_all_conditions_4_gender.png')

# Figure 1C (Stable)
scr = figure1.getballistictrials(cr)
scr = scr.query('session in [3,4]')
sinfo = info.query('session in [3,4]')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,label=['stable'],fname='all_subjects_duration_maxheight_stable.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_stable_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_stable_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_stable_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_stable_gender.png')

# Figure 1C (Partial)
scr = figure1.getballistictrials(cr)
scr = scr.query('session in [9,10]')
sinfo = info.query('session in [9,10]')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,color='r',label=['partial'],fname='all_subjects_duration_maxheight_partial.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_partial_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_partial_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_partial_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_partial_gender.png')

# Figure 1C (Unstable)
scr = cr.query('session not in [3,4,9,10]')
sinfo = info.query('session not in [3,4,9,10]')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_0.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_1_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_2_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_3_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_4_gender.png')

# Figure 1D (Across Conditions+ DECORTICATES)
cr = activitytables.read_subjects(subjects,days=range(1,5),
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects,days=range(1,5),
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1d'
figure1.figure1d(cr,info,fbase)

# Figure 1D (Across Conditions)
cr = activitytables.read_subjects(subjects[1:],days=None,
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=None,
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1d'
figure1.figure1d(cr,info,fbase)

# Figure 1D2 (Across Conditions)
fbase = r'C:\figs\figure1d2'
figure1.figure1d2(cr,info,fbase)

# Figure 1F (Random)
fbase = r'C:\figs\figure1f_random_week'
cr = activitytables.read_subjects(subjects[1:],days=[3,4,9,10],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,15,16],
                                    key=activitytables.info_key)
figure1.figure1f(cr,fbase)
#figure1.figure1f2(cr, fbase)

# Figure 1F3 (Pooled Session Trajectories)
fbase = r'C:\figs\figure1f_random_week'
cr = activitytables.read_subjects(subjects[1:],days=[3,4,9,10],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,15,16],
                                    key=activitytables.info_key)
figure1.figure1f3(cr,fbase)

# Figure 1F (Stable vs Random Stable)
# Need to fix figure1
fbase = r'C:\figs\figure1f_week1_vs_weekR_stable_trials'
stcr = cr.query('session in [3,4]')
rcr = cr.query('session in [15,16] and stepstate3').copy()
rcr.stepstate3 = False
rcr.stepstate4 = False
tcr = pd.concat((stcr,rcr))
figure1.figure1f2(tcr, fbase)

# Figure 1F3 (Component-by-component over time Stable vs Random Stable)
# Need to fix figure1
fbase = r'C:\figs\figure1f3_componentovertime'
rcr = cr.query("subject != 'JPAK_20' and session in [13,14,15,16]").copy()
figure1.figure1f2(rcr, fbase)

# Figure 1I (Stable)
fbase = r'C:\figs\figure1i'
cr = activitytables.read_subjects(subjects,days=range(1,5),
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects,days=range(1,5),
                                    key=activitytables.info_key)
figure1.figure1i(cr,fbase)

# Figure 1I (Partial)
cr = activitytables.read_subjects(subjects[1:],days=range(6,12),
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=range(6,12),
                                    key=activitytables.info_key)
figure1.figure1i(cr,fbase)

# Figure 1I (Stable vs Partial)
cr = activitytables.read_subjects(subjects[1:],days=[3,4,9,10],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,9,10],
                                    key=activitytables.info_key)
figure1.figure1i2(cr,fbase)

# Figure 1J (Stable vs Partial Skip/Step)
fbase = r'C:\figs\figure1j'
figure1.figure1j(info,fbase)

# Figure 1K (Stable and Partial Postures)
fbase = r'C:\figs\figure1k'
figure1.figure1k(info,fbase)

# Figure 1K1 (Representative Postures)
figure1.figure1k1(info,fbase)

# Figure 1K2 (First Step Postures)
figure1.figure1k2(info,fbase)

# Figure 1K3 (Slip analysis - CRUDE)
fbase = r'C:\figs\figure1k4'
info = activitytables.read_subjects(subjects,days=range(1,5),
                                    key=activitytables.info_key)
ss = figure1.figure1k4(info,fbase)

# Figure 1L (Stable vs Partial)
info = activitytables.read_subjects(subjects[1:],days=[3,4,9,10],
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1l'
figure1.figure1l(info,fbase)

# Figure 1L2 (Stable vs Partial POOLED)
fbase = r'C:\figs\figure1l2'
figure1.figure1l2(info,fbase)

# Figure 1L3 (Stable vs Partial Across Sessions POOLED)
info = activitytables.read_subjects(subjects[1:],days=range(1,6),
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1l3'
figure1.figure1l2(info.query('session == 1'),fbase)
figure1.figure1l2(info.query('session == 2'),fbase)
figure1.figure1l2(info.query('session == 3'),fbase)
figure1.figure1l2(info.query('session == 4'),fbase)
figure1.figure1l2(info.query('session == 5'),fbase)

# Figure 1L4 (Stable vs Unstable Trials Across RANDOM POOLED - LESION/SHAM)
info = activitytables.read_subjects(subjects[1:],days=range(13,17),
                                    key=activitytables.info_key)
lesionmask = (info.lesionleft + info.lesionright) > 0
lesions = info[lesionmask]
controls = info[~lesionmask]
ixsts = pd.read_hdf(r'C:/figs/steptraces.hdf5','stable')
uxsts = pd.read_hdf(r'C:/figs/steptraces.hdf5','unstable')
lquery = lesions.index.levels[0][lesions.index.labels[0]].unique()
cquery = controls.index.levels[0][controls.index.labels[0]].unique()
lquery = repr(lquery).replace('array(','').replace(', dtype=object)','').replace('\n','')
cquery = repr(cquery).replace('array(','').replace(', dtype=object)','').replace('\n','')
lixsts = ixsts.query(str.format("subject in {0}",lquery))
luxsts = uxsts.query(str.format("subject in {0}",lquery))
cixsts = ixsts.query(str.format("subject in {0}",cquery))
cuxsts = uxsts.query(str.format("subject in {0}",cquery))
fbase = r'C:\figs\figure1l4\all'
p = [figure1.figure1l2(info,
                       fbase,
                       ixsts[ixsts.frameindex == (200 + i * 5)],
                       uxsts[uxsts.frameindex == (200 + i * 5)],str(i))
                       for i in range(15)]
fbase = r'C:\figs\figure1l4\lesions'
p = [figure1.figure1l2(lesions,
                       fbase,
                       lixsts[lixsts.frameindex == (200 + i * 5)],
                       luxsts[luxsts.frameindex == (200 + i * 5)],str(i))
                       for i in range(15)]
fbase = r'C:\figs\figure1l4\controls'
p = [figure1.figure1l2(controls,
                       fbase,
                       cixsts[cixsts.frameindex == (200 + i * 5)],
                       cuxsts[cuxsts.frameindex == (200 + i * 5)],str(i))
                       for i in range(15)]
#figure1.figure1l2(info,fbase)
                       
# Figure 1L5 (Stable vs Unstable Trials Temporal Averages RANDOM POOLED)
plt.figure()
q = "subject in ['JPAK_22','JPAK_24']"
st21 = ixsts.query(q)
u21 = uxsts.query(q)
activityplots.xplot(st21,'yhead','b')
activityplots.xplot(u21,'yhead','r')

p = [plot(activitytables.max_width_cm - g.xhead,'k',alpha=0.2)
     for i,g in ixsts.query("subject == 'JPAK_21' and session == 13 and side == 'leftwards'") \
                     .groupby('crossindex')]
p = [plot(g.xhead,'k',alpha=0.2)
     for i,g in ixsts.query("subject == 'JPAK_21' and session == 13 and side == 'rightwards'") \
                     .groupby('crossindex')]

# Figure 1L4 (Stable vs Unstable Trials Across RANDOM POOLED)
info = activitytables.read_subjects(subjects[1:],days=range(13,17),
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1l4'
figure1.figure1l2(info,fbase)

# Figure 1M (DEBUG Manipulation Clips)
l = 'leftwards'
r = 'rightwards'
fbase = r'C:\figs\figure1m'
firststepsleft = [{'frame':[9598,15988,18917,23803,30108],'side':[l,l,l,l,l]},
                  {'frame':[5493,12380,18340,35465,43856],'side':[l,l,l,l,l]},
                  {'frame':[4781,8822,12731,16807,22239],'side':[l,l,l,l,l]},
                  {'frame':[4882,8838,13545,19231,25905],'side':[l,l,l,l,l]},
                  {'frame':[5048,11478,16339,22546,31033],'side':[l,l,l,l,l]},
                  {'frame':[11062,15837,20908,25790,31137],'side':[l,l,l,l,l]},
                  {'frame':[6570,12109,18810,25098,35070],'side':[l,l,l,l,l]},
                  {'frame':[5226,8528,11337,16790,22740],'side':[l,l,l,l,l]},
                  {'frame':[6581,13707,19297,26235,36854],'side':[l,l,l,l,l]},
                  {'frame':[12580,20847,31621,42846,57694],'side':[l,l,l,l,l]},
                  {'frame':[4245,9791,16398,24656,31783],'side':[l,l,l,l,l]},
                  {'frame':[10165,17579,25543,30403,42213],'side':[l,l,l,l,l]},
                  {'frame':[7676,13523,18356,28951,34124],'side':[l,l,l,l,l]},
                  {'frame':[6186,14168,19739,26224,32900],'side':[l,l,l,l,l]},
                  {'frame':[5057,9776,13048,21717,36839],'side':[l,l,l,l,l]},
                  {'frame':[8362,14830,18357,33320,38820],'side':[l,l,l,l,l]},
                  {'frame':[8652,17459,21512,30347,35168],'side':[l,l,l,l,l]},
                  {'frame':[13777,23882,30507,36347,44263],'side':[l,l,l,l,l]},
                  {'frame':[5872,9864,15068,20186,28168],'side':[l,l,l,l,l]},
                  {'frame':[12992,17832,26694,30593,38165],'side':[l,l,l,l,l]},
                  {'frame':[6107,10056,14898,18434,24263],'side':[l,l,l,l,l]},
                  {'frame':[9091,12196,19427,29414,37746],'side':[l,l,l,l,l]}]

firststeps = [{'frame':[9598,11914,15988,17432,18917],'side':[l,r,l,r,l]},
              {'frame':[5493,8200,12380,13584,18340],'side':[l,r,l,r,l]},
              {'frame':[4781,6781,8822,10963,12731],'side':[l,r,l,r,l]},
              {'frame':[4882,6948,8838,10070,13545],'side':[l,r,l,r,l]},
              {'frame':[5048,8074,11478,13386,16339],'side':[l,r,l,r,l]},
              {'frame':[11062,14035,15837,18391,20908],'side':[l,r,l,r,l]},
              {'frame':[6570,10110,12109,15427,18810],'side':[l,r,l,r,l]},
              {'frame':[5226,6596,8528,9935,11337],'side':[l,r,l,r,l]},
              {'frame':[6581,8914,13707,16453,19297],'side':[l,r,l,r,l]},
              {'frame':[12580,15257,20847,27342,31621],'side':[l,r,l,r,l]},
              {'frame':[4245,6565,9791,12862,16398],'side':[l,r,l,r,l]},
              {'frame':[10165,11735,17579,21866,25543],'side':[l,r,l,r,l]},
              {'frame':[7676,10867,13523,15892,18356],'side':[l,r,l,r,l]},
              {'frame':[6186,9075,14168,17987,19739],'side':[l,r,l,r,l]},
              {'frame':[5057,7080,9776,11300,13048],'side':[l,r,l,r,l]},
              {'frame':[8362,11371,14830,16943,18357],'side':[l,r,l,r,l]},
              {'frame':[8652,14440,17459,19832,21512],'side':[l,r,l,r,l]},
              {'frame':[13777,17682,23882,27264,30507],'side':[l,r,l,r,l]},
              {'frame':[5872,8290,9864,11833,15068],'side':[l,r,l,r,l]},
              {'frame':[12992,15174,17832,22024,26694],'side':[l,r,l,r,l]},
              {'frame':[6107,8033,10056,12672,14898],'side':[l,r,l,r,l]},
              {'frame':[9091,12196,19427,24159,29414],'side':[l,l,l,r,l]}]
act = activitytables.read_subjects(subjects,days=[0],includeinfokey=False)
cr = activitytables.read_subjects(subjects,days=[0],
                                  selector=lambda x:activitytables.crossings(x,True,True))
info = activitytables.read_subjects(subjects,days=[0],
                                    key=activitytables.info_key)
figure1.figure1m(firststeps,info,fbase)

# Figure 1N (Slip clustering)
info = activitytables.read_subjects(subjects,days=[3,4],
                                    key=activitytables.info_key)
fbase = r'C:\figs\figure1n'
figure1.figure1n(info,fbase)

# Figure 1O (Center ROI Profiles)
info = activitytables.read_subjects(subjects,key=activitytables.info_key)
stable = info.query('session > 0 and session < 5').copy(True)
centerfree = info.query("protocol == 'centerfree'").copy(True)
random = info[info.protocol.str.contains('randomizedcenterfree_')].copy(True)
permutations = info[info.protocol.str.contains('permutationfreepair')].copy(True)
fullyreleased = info[info.protocol.str.contains('fullyreleased')].copy(True)
random.protocol = 'randomizedcenterfree'
permutations.protocol = 'permutations'
fullyreleased.protocol = 'fullyreleased'
fbase = r'C:\figs\figure1o2'
strials = figure1.figure1o(stable,fbase)
utrials = figure1.figure1o(centerfree,fbase)
rtrials = figure1.figure1o(random,fbase)
ptrials = figure1.figure1o(permutations,fbase)
ftrials = figure1.figure1o(fullyreleased,fbase)
time = np.arange(-60,+180) / figure1.frames_per_second
bigstrials = np.concatenate(strials,axis=1).mean(axis=1)
bigutrials = np.concatenate([u for u in utrials if len(u) > 0],axis=1).mean(axis=1)
bigrtrials = np.concatenate(rtrials,axis=1).mean(axis=1)
bigptrials = np.concatenate(ptrials,axis=1).mean(axis=1)
bigftrials = np.concatenate(ftrials,axis=1).mean(axis=1)
fig = plt.figure()
plt.plot(time,bigstrials,'g',label='stable')
plt.plot(time,bigutrials,'r',label='partial')
plt.plot(time,bigrtrials,'m',label='random')
plt.plot(time,bigptrials,'y',label='permutations')
plt.plot(time,bigftrials,'b',label='full')
plt.legend()
plt.xlabel('time (s)')
plt.ylabel('step activity (A.U.)')
fname = str.format("averagestepactivity.png")
fpath = os.path.join(fbase,fname)
plt.savefig(fpath)
plt.close(fig)

# Normalize avg
def normalizeavg(trials):
    maxtrials = trials.max(axis=0)
    ntrials = trials / maxtrials
    return ntrials.mean(axis=1),ntrials
savg = normalizeavg(strials)
uavg = normalizeavg(utrials)
ravg = normalizeavg(rtrials)
pavg = normalizeavg(ptrials)
favg = normalizeavg(ftrials)



# Figure 2 (Ethograms)
act = activitytables.read_subjects(subjects,days=[5],includeinfokey=False)
cr = activitytables.read_subjects(subjects,days=[5],
                                  selector=lambda x:activitytables.crossings(x,True,False))
#cr = activitytables.read_subjects(subjects,days=[5],
#                                  selector=lambda x:activitytables.crossings(x,False,False))
rr = activitytables.read_subjects(subjects,days=[5],
                                  key=activitytables.rewards_key)
info = activitytables.read_subjects(subjects,days=[5],
                                    key=activitytables.info_key)

# Figure 2A (Ethogram aligned on stretch)
fbase = r'C:\figs\figure2a'
manipulations = [{'frame':[59652,62973],'side':[l,l]},
                 {'frame':[50916,58294],'side':[l,l]},
                 {'frame':[34416,37161],'side':[l,l]},
                 {'frame':[56067,59295],'side':[l,l]}]
figure1.figure2a(manipulations,info,fbase)
figure1.figure2a2(act,cr,info,fbase)

# Figure 2A3 (Biggest manipulation clip)
figure1.figure2a3(act,info,fbase)

# Figure 2B (Manipulation Clips)
fbase = r'C:\figs\figure2b'
figure1.figure2b(act,cr,info,fbase)

# Figure 2C (Lifetime Clips)
fbase = r'C:\figs\figure2c'
cr = activitytables.read_subjects(subjects,selector=activitytables.crossings)
info = activitytables.read_subjects(subjects,key=activitytables.info_key)
figure1.figure2c(cr,info,fbase)
figure1.figure2c2(cr,info,fbase)

# Figure 2C2 (Lifetime Clips Off-center)
fbase = r'C:\figs\figure2c2'
center23 = (activitytables.stepcenter_cm[3][1] + \
            activitytables.stepcenter_cm[2][1]) / 2
center45 = (activitytables.stepcenter_cm[4][1] + \
            activitytables.stepcenter_cm[5][1]) / 2
cr = activitytables.read_subjects(subjects,
                                  selector=lambda x:activitytables.crossings(x,center=center23))
info = activitytables.read_subjects(subjects,key=activitytables.info_key)
figure1.figure2c(cr,info,fbase)
figure1.figure2c2(cr,info,fbase)
                                    
# Figure 2E (Time to reward)
fbase = r'C:\figs\figure2e'
figure1.figure2e(act,cr,rr,info,fbase)