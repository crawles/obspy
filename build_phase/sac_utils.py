from obspy import *
import os
import sys
import numpy
import datetime
from numpy import *

def read_sac_dir(sac_input):
    """ Reads SAC files into directory. Input is a SAC file or directory. 
    Returns a list where each element is a stream, which contains an indivual
    trace
    """
    trace_list = []
    if os.path.isdir(sac_input):
        for dirname, dirnames, filenames in os.walk(sac_input):
            # print path to all subdirectories first.
            #for subdirname in dirnames:
            #    print os.path.join(dirname, subdirname)

            # build list of traces.
            for filename in filenames:
                try:
                    sac_file = os.path.join(dirname, filename)
                    seismogram = read(sac_file)
                    seismogram[0].stats.update({'file':filename})
                    trace_list.append(seismogram[0])
                except:
                    pass
            return trace_list
    else:
        seismogram = read(sac_input)
        trace_list.append(seismogram[0])
        return trace_list

def group_stations_for_event(list_of_traces):
    """ returns a list where each element is a list of traces for a
    given station """
    stations = []
    station = []
    prev_station_name = 'abc'
    for trace in list_of_traces:
        cur_station_name = trace.stats.station
        if cur_station_name == prev_station_name:
            station.append(trace)
        elif cur_station_name != prev_station_name: 
            stations.append(station)
            station = []
            station.append(trace)
        prev_station_name = cur_station_name
    stations.append(station)
    stations.pop(0)
    return stations

def find_trace_with_same_file_name(trace, list_of_traces):
    """ return trace with name file name"""
    try:
        for f in list_of_traces:
            if f.stats.file == trace.stats.file:
                return f
    except:
        raise("No matching trace")

