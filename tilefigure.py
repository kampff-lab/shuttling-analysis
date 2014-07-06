# -*- coding: utf-8 -*-
"""
Created on Sat Jun 08 21:13:03 2013

@author: gonca_000
"""
from win32api import GetSystemMetrics

def tilefigures(figures,layout):
    screenwidth = GetSystemMetrics(0)
    screenheight = GetSystemMetrics(1)
    figwidth = screenwidth / layout[0]
    figheight = screenheight / layout[1]
    
    for i,fig in enumerate(figures):
        x = i % layout[0]
        y = i / layout[0]
        manager = fig.canvas.manager
        manager.window.setGeometry(x*figwidth,y*figheight,figwidth,figheight)