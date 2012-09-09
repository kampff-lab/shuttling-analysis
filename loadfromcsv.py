# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import csv
import string

def loadfromcsv(filename,convert=lambda x:float(x)):
    with open(filename) as file:
        return [[convert(x) for x in string.split(line[0])] for line in csv.reader(file)]