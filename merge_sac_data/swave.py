from obspy import *
import os
import sys
import numpy
import datetime
from numpy import *

def pick_quality(trace,wave_type):
    """ Outputs quality of pick for P and S waves"""
    # Determine wave type.
    if wave_type == "s" or wave_type == "S":
        marker = "kt0"
    elif wave_type == "p" or wave_type == "P":
        marker = "a"
    else:
        raise Exception("incorrect wave type")
    # Return quality, if exists.
    pick_stats = eval("trace.stats.sac."+marker+".rstrip()")
    if len(pick_stats) == 4:
        quality = int(pick_stats[-1])
        return quality
    else:
        raise Exception("No quality pick")
def get_Spick_quality(trace):
    kt0 = trace.stats.sac.kt0
    qual = int(kt0[3])
    return qual

def get_true_time(trace, when):
    """ Adds relative when time to absolute trace time."""
    if when == 'o' or when == 'O':
        return trace.stats.starttime
    elif when == 'p' or when == 'P':
        return trace.stats.starttime + trace.stats.sac.a
    elif when == 's' or when == 'S':
        return trace.stats.starttime + trace.stats.sac.t0
    elif type(when) == float:
        return trace.stats.starttime + when
    else:
        raise Exception("Not valid type.")

def modify_trace_window_ps(trace,beg_delta,end_delta):
    """Cuts trace. No output, just modifies trace object. """
    p = trace.stats.sac.a
    s = trace.stats.sac.t0
    if (s-p) <= 0 or (s-p) > 10:
        raise Exception("Not valid picks")
    
    t0 = trace.stats.starttime
    p_wave = t0 + float(p)
    s_wave = t0 + float(s)
    trace.trim(p_wave + float(beg_delta), s_wave + (end_delta))

def modify_trace_window_around_point(trace,point_time,
        before_delta,after_delta):
    """Cuts trace around a point in time"""
    trace.trim(point_time - abs(before_delta), point_time + abs(after_delta))

def filter_stream_if_has_quality_pick(sac_stream):
    """ PARKFIELD Returns list, all of events, which have manual picks """ 
    filtered_stream=[]
    for trace in sac_stream:
        try:
            q = pick_quality(trace,"S")
            filtered_stream.append(trace)
        except:
            pass
    return filtered_stream

def filter_stream_if_has_quality_pick(sac_stream):
    """ ALPINE Returns list, all of events, which have manual picks """ 
    filtered_stream=[]
    for trace in sac_stream:
        if trace.stats.sac.t2 != -12345.0:
            filtered_stream.append(trace)
    return filtered_stream

def filter_stream_if_has_sample_rate(streams,sample_rate):
    """ Returns list, all of events, which have manual picks """ 
    filtered_stream=[]
    for trace in streams:
            if trace.stats.delta == sample_rate:
                filtered_stream.append(trace)
    return filtered_stream

def randomly_trim_streams(streams,window_length):
    """ Returns list, all of events, which have manual picks """ 
    filtered_stream=[]
    for trace in streams:
        if len(trace)>=window_length:
            starting_pt = random.randint(0,(len(trace)-window_length))
            trace_cut = trim_trace(trace,window_length,starting_pt)
            filtered_stream.append(trace_cut)
    return filtered_stream

def rmean(trace):
    trace.data = trace.data - trace.data.mean()
    return trace

    
#def oet_trace_dist(s,t):
#    """ compute distance between to .data arrays of equal length"""
#    D = 0.0
#    for s_pt,t_pt in zip(s.data,t.data):
#        D = D + float(s_pt - t_pt)**2
#    return D


def prob_class(dist_list,y):
    """Using the distances of an observation to the reference signals 
    of a certain class, compute a number proportional to the probability
    that the observation belongs to that class."""
    P = 0
    for dist in dist_list:
        P = P + exp(-y*dist)
    return P


def bin_trace(s, bin_size):
    binned_data = numpy.array(zeros(len(s.data)/bin_size))
    i = 0
    j = 0
    bpt = 0
    for pt in s.data:
        i = i + 1
        bpt = bpt + pt
        if i >= bin_size:
            binned_data[j] = bpt/bin_size
            bpt = 0
            j = j + 1
            i = 0
    s.stats.sampling_rate = s.stats.sampling_rate/bin_size
    s.data = binned_data
    return s

def trim_trace(trace,window_length,i):
    s = trace.copy()
    t = s.stats.starttime
    time_window_beg = t + i*s.stats.delta
    time_window_end = time_window_beg + (window_length*s.stats.delta) - s.stats.delta
    s.trim(time_window_beg,time_window_end)
    return s

def classify_obs(s,Rpos,Rneg,gamma,theta,norm_type):
    a = datetime.datetime.now()
    s = normalize_trace(s,norm_type,1)
    d_pos_list = get_trace_dist_list(s,Rpos,norm_type)
    d_neg_list = get_trace_dist_list(s,Rneg,norm_type)
    b = datetime.datetime.now()
    #print b - a
    R = prob_class(d_pos_list,.01)/prob_class(d_neg_list,.01)
    pos_class = 0
    if R > theta:
        pos_class = 1
    return [R,pos_class]

def classify_trace(trace,window_length,time_interval,pos_set,neg_set,bin_size,norm_type):
    """Classifies trace by using a sliding time window for a specfied 
    interval and window size."""

    num_of_windows = time_interval[1]- time_interval[0]
    time_window_beg = time_interval[0]
    i=0
    r_list = numpy.array(zeros(num_of_windows*bin_size))

    while i < num_of_windows:
        #Create window of trace
#        print trace.stats.starttime,trace.stats.endtime
        s = trim_trace(trace,window_length,i+time_window_beg)
#        print s.stats.starttime,s.stats.endtime,s.stats
#        raw_input()
        if i + window_length > len(trace.data):
            raise Exception(window_length > trace.data)

        [r,pos_signal] = classify_obs(s,pos_set,neg_set,2,10,norm_type)
        for bin_num in range(bin_size):
            r_list[(bin_size*i)+bin_num] = r
        i = i + 1

    return r_list

def get_trace_dist_list(s,ref_set,norm_type):
    """returns a list of distances for the ref_set"""
#    s = normalize_trace(s,norm_type,1)
    dist_list = numpy.array(zeros(len(ref_set)))
    i = 0
    for r in ref_set:
        D = sum((s.data-r.data)**2)
        qual = get_Spick_quality(r) 
        weight = get_weighted_dist_coefficient(qual)
        dist_list[i] = weight*D
        i = i + 1
    
    return dist_list


def get_weighted_dist_coefficient(qual):
    return (10-qual)/10.0

def normalize_trace(trace,norm_type,scale_val=0):
    """applies 1,2 norm and then normalizes data using max"""
    if norm_type == 0:
        pass
    elif norm_type == 1:
        trace.data = abs(trace.data)
    elif norm_type == 2:
        trace.data = abs(trace.data)**2
    if scale_val == 0:
        scale_val = max(abs(trace.data))
    elif scale_val == 1:
        scale_val = mean(trace.data[0:(len(trace.data)/2)])
    trace.data = trace.data/scale_val
    return trace
