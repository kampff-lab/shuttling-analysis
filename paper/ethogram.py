# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 16:28:54 2013

@author: kampff
"""

import utils
import datetime
import itertools
import numpy as np
import dateutil.parser as parser
import matplotlib.pyplot as plt

EventType = {'WindowOpening':'Onset','WindowClosing':'Offset','PointEvent':'Point'}

class Event:
    def __init__(self,timestamp,name=None,eventType=None):
        if eventType is None:
            if name.endswith('Offset'):
                eventType = 'Offset'
                name = name[:name.find('Offset')]
            elif name.endswith('Onset'):
                eventType = 'Onset'
                name = name[:name.find('Onset')]
            else:
                eventType = 'Point'
        self.name = name
        self.timestamp = parser.parse(timestamp)
        self.type = eventType
        
    def __repr__(self):
        return "Event({0},{1},{2})".format(self.name,self.timestamp,self.type)
        
    __str__ = __repr__
        
def load_events(path,eslice=slice(None),delimiter=None):
    with open(path) as eventfile:
        eventdata = np.genfromtxt(itertools.islice(eventfile,eslice.start,eslice.stop,eslice.step),dtype=str,delimiter=delimiter)
        eventdata = utils.ensure_list(eventdata)
    datashape = np.shape(eventdata)
    if len(datashape) == 1:
        columns = 1 if datashape[0] > 0 else 0
    else:
        columns = datashape[1]
    
    if columns < 1 or columns > 3:
        raise ValueError('event file must have between 1 and 3 columns')
        
    if columns == 1:
        events = [Event(data) for data in eventdata]
        
    if columns == 2:
        try:
            parser.parse(eventdata[0,0],default=42)
            events = [Event(data[0],None,EventType[data[1]]) for data in eventdata]
        except:
            events = [Event(data[1],data[0]) for data in eventdata]
        
    if columns == 3:
        events = [Event(data[1],data[0],EventType[data[2]]) for data in eventdata]
        
    if len(events) == 1:
        return events[0]
    return np.array(events)

def get_event_groups(events):
    keyfunc = lambda x:x.name
    return itertools.groupby(sorted(events,key=keyfunc),keyfunc)
    
def get_event_overlap(duration1,duration2):
    onset1 = duration1[0]
    onset2 = duration2[0]
    offset1 = onset1 + duration1[1]
    offset2 = onset2 + duration2[2]
    
    # If event finishes before the other starts, no overlap
    if offset1 < onset2:
        return None
    
    # Overlap onset happens when second event starts
    onsetoverlap = onset2

    # Second event finishes before first event finishes    
    if offset2 < offset1:
        overlapduration = offset2
    else:
        # Second event finishes after first event finishes
        overlapduration = offset1 - onset2
    
    return onsetoverlap, overlapduration
    
def get_event_durations(events):
    for i, event in enumerate(events):
        if event.type == 'Point':
            yield event, datetime.timedelta()
        elif event.type == 'Onset':
            offset = next(offset for offset in itertools.islice(events,i+1,None) if offset.name == event.name)
            yield event, offset.timestamp - event.timestamp
                
def plot_events(events,name=None,xoffset=None,yoffset=0,color=None,**kwargs):
    if xoffset is None:
        xoffset = events[0].timestamp
    durations = get_event_durations(events)
    ranges = [((event.timestamp - xoffset).total_seconds(), duration.total_seconds()) for event,duration in durations]
    plt.broken_barh(ranges,[yoffset,1],label=name,color=color,**kwargs)
    
def plot_event_sets(eventsets,names=None,xoffset=None,yoffset=0,yoffsetscale=1,colors=None,**kwargs):
    if names is None:
        names = iter(lambda:None,1)
        
    if colors is None:
        colors = iter(lambda:None,1)        
        
    for i, (events, name, color) in enumerate(itertools.izip(eventsets,names,colors)):
        plot_events(events,name=name,xoffset=xoffset,yoffset=i*yoffsetscale+yoffset,color=color,**kwargs)