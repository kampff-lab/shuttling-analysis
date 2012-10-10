# -*- coding: utf-8 -*-
"""
Created on Tue Jun 05 16:13:44 2012

@author: IntelligentSystems
"""

import os
import parse_session as parser
import analysis_utilities as utils

def load_path(basefolder):
    sessions = []
    datafolders = [path + '\\Analysis' for path in utils.directory_tree(basefolder,1)]
    for path in datafolders:
        path_parts = os.path.split(path)
        subject = path_parts[1]
        date = os.path.split(path_parts[0])[1]
        sessions.append(parser.parse_session(path,subject + ' ' + date))
    return sessions
    
def annotate_jpak345(sessions):
    sessions[0].session_type = 'habituation'
    for i in range(5):
        sessions[i].session_type += ' (lowered)'
    sessions[9].session_type += ' (servos)'
    for i in range(10,14):
        sessions[i].session_type += ' (5th step acw)'
    for i in range(16,18):
        sessions[i].session_type += ' (4th step cw)'
    for i in range(19,22):
        sessions[i].session_type += ' (both)'
        
def annotate_jpak678(sessions):
    sessions[0].session_type = 'habituation'
    for i in range(5,14):
        sessions[i].session_type += ' (4th step cw)'
    for i in range(16,18):
        sessions[i].session_type += ' (4th step cw)'
    for i in range(19,22):
        sessions[i].session_type += ' (both)'
        
#==============================================================================
# jpak03 = True
# if jpak03:
#     #jpak03habituation = load_path('../Data/JPAK_03/2012_04_24-13_26/Analysis', 'jpak03habituation',False,False)
#     jpak03learning1 = load_path('../Data/JPAK_03/2012_04_25-14_46/Analysis', 'jpak03learning1',False,False)
#     jpak03learning2 = load_path('../Data/JPAK_03/2012_04_26-15_41/Analysis', 'jpak03learning2',False,False)
#     jpak03learning3 = load_path('../Data/JPAK_03/2012_04_28-16_57/Analysis', 'jpak03learning3',False,False)
#     jpak03learning4 = load_path('../Data/JPAK_03/2012_04_29-15_13/Analysis', 'jpak03learning4',False,False)
#     jpak03control1 = load_path('../Data/JPAK_03/2012_05_21-18_38/Analysis', 'jpak03control1')
#     jpak03control2 = load_path('../Data/JPAK_03/2012_05_22-20_45/Analysis', 'jpak03control2')
#     jpak03control3 = load_path('../Data/JPAK_03/2012_05_23-19_46/Analysis', 'jpak03control3')
#     jpak03control4 = load_path('../Data/JPAK_03/2012_05_25-00_04/Analysis', 'jpak03control4')
#     jpak03premanip = load_path('../Data/JPAK_03/2012_05_27-19_07/Analysis', 'jpak03premanip')
#     jpak03manip1 = load_path('../Data/JPAK_03/2012_05_28-19_20/Analysis', 'jpak03manip1',True)
#     jpak03manip2 = load_path('../Data/JPAK_03/2012_05_29-14_22/Analysis', 'jpak03manip2',True)
#     jpak03manip3 = load_path('../Data/JPAK_03/2012_05_30-15_25/Analysis', 'jpak03manip3',True)
#     jpak03manip4 = load_path('../Data/JPAK_03/2012_05_31-15_48/Analysis', 'jpak03manip4',True)
#     jpak03manip5 = load_path('../Data/JPAK_03/2012_06_19-10_32/Analysis', 'jpak03manip5',True)
#     jpak03stable1 = load_path('../Data/JPAK_03/2012_06_20-10_58/Analysis', 'jpak03stable1',False)
#     jpak03forwardrot1 = load_path('../Data/JPAK_03/2012_06_21-10_46/Analysis', 'jpak03forwardrot1',True)
#     jpak03forwardrot2 = load_path('../Data/JPAK_03/2012_06_22-12_55/Analysis', 'jpak03forwardrot2',True)
#     jpak03stable2 = load_path('../Data/JPAK_03/2012_07_03-11_41/Analysis', 'jpak03stable2',False)
#     jpak03learning = process_session.merge_sessions('jpak03learning',[jpak03learning1,jpak03learning2,jpak03learning3,jpak03learning4])
#     jpak03control = process_session.merge_sessions('jpak03control',[jpak03control1,jpak03control2,jpak03control3,jpak03control4])
#     jpak03manipA = process_session.merge_sessions('jpak03manip1',[jpak03premanip, jpak03manip1,jpak03manip2,jpak03manip3,jpak03manip4])
#     jpak03manipB = process_session.merge_sessions('jpak03manip2',[jpak03forwardrot1,jpak03forwardrot2])
# 
# jpak04 = False
# if jpak04:
#     #jpak04habituation = load_path('../Data/JPAK_04/2012_04_24-13_44/Analysis', 'jpak04habituation',False,False)
#     jpak04learning1 = load_path('../Data/JPAK_04/2012_04_25-15_21/Analysis', 'jpak04learning1',False,False)
#     jpak04learning2 = load_path('../Data/JPAK_04/2012_04_26-16_19/Analysis', 'jpak04learning2',False,False)
#     jpak04learning3 = load_path('../Data/JPAK_04/2012_04_28-17_40/Analysis', 'jpak04learning3',False,False)
#     jpak04learning4 = load_path('../Data/JPAK_04/2012_04_29-17_08/Analysis', 'jpak04learning4',False,False)
#     jpak04control1 = load_path('../Data/JPAK_04/2012_05_21-19_13/Analysis', 'jpak04control1')
#     jpak04control2 = load_path('../Data/JPAK_04/2012_05_22-21_19/Analysis', 'jpak04control2')
#     jpak04control3 = load_path('../Data/JPAK_04/2012_05_23-20_21/Analysis', 'jpak04control3')
#     jpak04control4 = load_path('../Data/JPAK_04/2012_05_25-00_40/Analysis', 'jpak04control4')
#     jpak04premanip = load_path('../Data/JPAK_04/2012_05_27-19_39/Analysis', 'jpak04premanip')
#     jpak04manip1 = load_path('../Data/JPAK_04/2012_05_28-19_59/Analysis', 'jpak04manip1',True)
#     jpak04manip2 = load_path('../Data/JPAK_04/2012_05_29-15_01/Analysis', 'jpak04manip2',True)
#     jpak04manip3 = load_path('../Data/JPAK_04/2012_05_30-16_09/Analysis', 'jpak04manip3',True)
#     jpak04manip4 = load_path('../Data/JPAK_04/2012_05_31-16_25/Analysis', 'jpak04manip4',True)
#     jpak04stable1 = load_path('../Data/JPAK_04/2012_06_19-11_09/Analysis', 'jpak04stable1',False)
#     jpak04stable2 = load_path('../Data/JPAK_04/2012_06_20-11_34/Analysis', 'jpak04stable2',False)
#     jpak04forwardrot1 = load_path('../Data/JPAK_04/2012_06_21-11_26/Analysis', 'jpak04forwardrot1',True)
#     jpak04forwardrot2 = load_path('../Data/JPAK_04/2012_06_22-13_31/Analysis', 'jpak04forwardrot2',True)
#     jpak04stable3 = load_path('../Data/JPAK_04/2012_07_03-12_21/Analysis', 'jpak04stable3',False)
#     jpak04learning = process_session.merge_sessions('jpak04learning',[jpak04learning1,jpak04learning2,jpak04learning3,jpak04learning4])
#     jpak04control = process_session.merge_sessions('jpak04control',[jpak04control1,jpak04control2,jpak04control3,jpak04control4])
#     jpak04manipA = process_session.merge_sessions('jpak04manip1',[jpak04premanip, jpak04manip1,jpak04manip2,jpak04manip3,jpak04manip4])
#     jpak04manipB = process_session.merge_sessions('jpak04manip2',[jpak04forwardrot1,jpak04forwardrot2])
# 
# jpak05 = False
# if jpak05:
#     #jpak05habituation = load_path('../Data/JPAK_05/2012_04_24-13_58/Analysis', 'jpak05habituation',False,False)
#     jpak05learning1 = load_path('../Data/JPAK_05/2012_04_25-15_55/Analysis', 'jpak05learning1',False,False)
#     jpak05learning2 = load_path('../Data/JPAK_05/2012_04_26-16_54/Analysis', 'jpak05learning2',False,False)
#     jpak05learning3 = load_path('../Data/JPAK_05/2012_04_28-18_12/Analysis', 'jpak05learning3',False,False)
#     jpak05learning4 = load_path('../Data/JPAK_05/2012_04_29-16_17/Analysis', 'jpak05learning4',False,False)
#     jpak05control1 = load_path('../Data/JPAK_05/2012_05_21-19_48/Analysis', 'jpak05control1')
#     jpak05control2 = load_path('../Data/JPAK_05/2012_05_22-21_50/Analysis', 'jpak05control2')
#     jpak05control3 = load_path('../Data/JPAK_05/2012_05_23-21_00/Analysis', 'jpak05control3')
#     jpak05control4 = load_path('../Data/JPAK_05/2012_05_25-01_15/Analysis', 'jpak05control4')
#     jpak05premanip = load_path('../Data/JPAK_05/2012_05_27-20_15/Analysis', 'jpak05premanip')
#     jpak05manip1 = load_path('../Data/JPAK_05/2012_05_28-20_31/Analysis', 'jpak05manip1',True)
#     jpak05manip2 = load_path('../Data/JPAK_05/2012_05_29-15_35/Analysis', 'jpak05manip2',True)
#     jpak05manip3 = load_path('../Data/JPAK_05/2012_05_30-16_43/Analysis', 'jpak05manip3',True)
#     jpak05manip4 = load_path('../Data/JPAK_05/2012_05_31-17_11/Analysis', 'jpak05manip4',True)
#     jpak05stable1 = load_path('../Data/JPAK_05/2012_06_19-11_50/Analysis', 'jpak05stable1',False)
#     jpak05stable2 = load_path('../Data/JPAK_05/2012_06_20-12_11/Analysis', 'jpak05stable2',False)
#     jpak05forwardrot1 = load_path('../Data/JPAK_05/2012_06_21-12_04/Analysis', 'jpak05forwardrot1',True)
#     jpak05forwardrot2 = load_path('../Data/JPAK_05/2012_06_22-14_06/Analysis', 'jpak05forwardrot2',True)
#     jpak05stable3 = load_path('../Data/JPAK_05/2012_07_03-13_27/Analysis', 'jpak05stable3',False)
#     jpak05learning = process_session.merge_sessions('jpak05learning',[jpak05learning1,jpak05learning2,jpak05learning3,jpak05learning4])
#     jpak05control = process_session.merge_sessions('jpak05control',[jpak05control1,jpak05control2,jpak05control3,jpak05control4])
#     jpak05manipA = process_session.merge_sessions('jpak05manip1',[jpak05premanip, jpak05manip1,jpak05manip2,jpak05manip3,jpak05manip4])
#==============================================================================
#    jpak05manipB = process_session.merge_sessions('jpak05manip2',[jpak05forwardrot1,jpak05forwardrot2])