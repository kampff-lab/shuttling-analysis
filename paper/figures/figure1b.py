# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 11:40:15 2013

@author: gonca_000
"""

import shuttling
import matplotlib.pyplot as plt

class figure1b:
    def __init__(self, lesions, controls):
        self.lesions = lesions
        self.controls = controls
        
    def plot(ax=None):
        if ax is None:
            ax = plt.axis()
            
        
            
def genfromtxt(lesionfolders,controlfolders):
    def gensessions(folders):
        return [shuttling.genfromtxt(path) for path in folders]
        
    def gensubjects(folders):
        return [gensessions(shuttling.findsessions(path)[1:4])
                for path in folders]
                    
    return figure1b(gensubjects(lesionfolders), gensubjects(controlfolders))