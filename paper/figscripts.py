# -*- coding: utf-8 -*-
"""
Created on Sun Nov 02 11:09:42 2014

@author: Gonçalo
"""

import figure1
import activitytables
import pandas as pd

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

cr = activitytables.read_subjects(subjects[1:],days=[3,4,9,10,-1],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,9,10,-1],
                                    key=activitytables.info_key)
                                    
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
scr = cr.query('session in [3,4]')
sinfo = info.query('session in [3,4]')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_0.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_1_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_2_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_3_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_4_gender.png')

# Figure 1C (Partial)
scr = cr.query('session in [9,10]')
sinfo = info.query('session in [9,10]')
scr = figure1.resetsessionindex(scr,[0,1,2],2)
sinfo = figure1.resetsessionindex(sinfo,[0,1,2],2)
figure1.figure1c0(scr,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_0.png')
figure1.figure1c3(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_1_lesion.png')
figure1.figure1c4(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_2_big_lesion.png')
figure1.figure1c5(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_3_weight.png')
figure1.figure1c6(scr,sinfo,fbase,alpha=alpha,fname='all_subjects_duration_maxheight_4_gender.png')

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

# Figure 1F (Random)
fbase = r'C:\figs\figure1f_random_week'
cr = activitytables.read_subjects(subjects[1:],days=[3,4,15,16],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects[1:],days=[3,4,15,16],
                                    key=activitytables.info_key)
figure1.figure1f(cr,fbase)
figure1.figure1f2(cr, fbase)

# Figure 1F (Stable vs Random Stable)
# Need to fix figure1
fbase = r'C:\figs\figure1f_week1_vs_weekR_stable_trials'
stcr = cr.query('session in [3,4]')
rcr = cr.query('session in [15,16] and stepstate3').copy()
rcr.stepstate3 = False
rcr.stepstate4 = False
tcr = pd.concat((stcr,rcr))
figure1.figure1f2(tcr, fbase)

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

# Figure 1L (Stable vs Partial)
fbase = r'C:\figs\figure1l'
figure1.figure1l(info,fbase)


# Figure 2 (Ethograms)
act = activitytables.read_subjects(subjects,days=[5])
cr = activitytables.read_subjects(subjects,days=[5],
                                  selector=activitytables.crossings)
info = activitytables.read_subjects(subjects,days=[5],
                                    key=activitytables.info_key)