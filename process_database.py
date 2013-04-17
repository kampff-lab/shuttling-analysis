# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:27:30 2013

@author: IntelligentSystems
"""

import csv
import dateutil

def load_database(path):
    with open(path,'rb') as csvfile:
        databasereader = csv.reader(csvfile)
        return [[dateutil.parser.parse(row[0]),row[1],row[2]] for row in databasereader]
        
def get_events(database,eventtype):
    return [event for event in database if event[1] == eventtype]
    
def get_closest_event(database,timestamp,condition=lambda evt:True):
    timestamps = [event[0] for event in database if condition(event)]
    if len(timestamps) == 0:
        return None
    index = min(range(len(timestamps)), key=lambda i: abs(timestamps[i]-timestamp))
    return database[index]
    
def get_closest_prior_event(database,timestamp):
    return get_closest_event(database,timestamp,lambda event:event[0] < timestamp)
    
def get_closest_post_event(database,timestamp):
    return get_closest_event(database,timestamp,lambda event:event[0] > timestamp)