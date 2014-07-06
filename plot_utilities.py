# -*- coding: utf-8 -*-
"""
Created on Wed Oct 09 14:09:10 2013

@author: IntelligentSystems
"""

import matplotlib.pyplot as plt

def hbracket(x,y,width,label=None,tickheight=1,color='k'):
    ax = plt.gca()
    ax.annotate(label,
            xy=(x, y), xycoords='data',
            xytext=(x, y+tickheight), textcoords='data',
            horizontalalignment='center',
            arrowprops=dict(arrowstyle="-[,widthB="+str(width), #linestyle="dashed",
                            color=color,
                            patchB=None,
                            shrinkB=0
                            ),
            )

def click_data_action(figure,ondataclick):
    def onclick(event):
        if event.button == 3 and event.xdata is not None and event.ydata is not None:
            ondataclick(event)
    figure.canvas.mpl_connect('button_press_event',onclick)
    
def fix_font_size():
    ax = plt.gca()
    plt.tight_layout()
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(15)