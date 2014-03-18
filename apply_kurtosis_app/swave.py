from obspy import *
import os
import sys
import copy
import numpy as np
import datetime
from numpy import *
from itertools import izip
import time

def get_relative_time(tr,absolute_time):
    time_from_beg = absolute_time - tr.stats.starttime
    time_from_b = time_from_beg + tr.stats.sac.b
    return time_from_b


def down_sample(trs):
    """down sample all traces to minimum sampling rate and remove, if neccessary,
    last element of array to make all traces have equal length """
    min_samp = sys.maxint
    min_len = sys.maxint
    for tr in trs:
        if tr.stats.sampling_rate < min_samp:
            min_samp = tr.stats.sampling_rate
        if len(tr) < min_len:
            min_len = len(tr)
    
    for tr in trs:
        samp_factor = int(tr.stats.sampling_rate/min_samp)
        if (samp_factor-(tr.stats.sampling_rate/min_samp)) > .001:
            raise Exception('factor is not integer')
        tr.decimate(factor = samp_factor,strict_length=False)

        delta_t = len(tr) - min_len
        if 1 < delta_t < 0:
            raise Exception('Not all of the traces are same length or sample rate')
#       tr.trim(endtime = tr.stats.endtime - delta_t/min_samp)
        tr.trim(starttime = tr.stats.starttime + delta_t/min_samp)

def update_stream_if_has_quality_pick(trs):
    """ Returns list, all of events, which have manual picks under t2 """ 
    updated_stream=[]
    for tr in trs:
        if tr.stats.sac.t2 and tr.stats.sac.t1 > 0:
            updated_stream.append(tr)
    return updated_stream

def sta_R(tr1,tr2):
    """get R using both components"""
    R1 = tr1.stats.R
    R2 = tr2.stats.R
    return R1*R2

def create_R_trace(tr,R):
    """ create a trace object with R as data for plotting,metrics """
    import copy
    R_tr = copy.deepcopy(tr)
    window_size = len(tr) - len(R)
    #trim off beg and end of R according to length of window size
    R_tr.data = (R_tr.data*0)+np.mean(R)
    R_tr.data[window_size/2:-window_size/2] = R
    return R_tr

def get_datetime():
    """e.g [March9,21:14:37]"""
    now = time.strftime("%c")
    date = str.split(now)[1]+str.split(now)[2]
    _time = str.split(now)[3]#h:m:s
    return [date,_time]
    
def print_one():
    pass

def trim_after_start_time(tr,beg,end):
    """cut time and edit b,e"""
    S = tr.stats.starttime
    E = tr.stats.endtime

    tr.trim(S + beg, S + end)

    S1 = tr.stats.starttime
    E1 = tr.stats.endtime
    
    tr.stats.sac.b = tr.stats.sac.b - (S-S1)
    tr.stats.sac.e = tr.stats.sac.e - (E-E1)  
    return tr

def pairwise(iterable):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

def get_x_val(trace,attribute):
    """ gets x position of input: t3,t4,etc.. """
    sr = trace.stats.sampling_rate
    t_rel = eval("trace.stats.sac." + attribute)
    t_tot = t_rel - trace.stats.sac.b
    x = int((round(sr*t_tot)))
    return x

def get_x_axis(tr):
    """ get x axis from cut trace"""
    sr = tr.stats.sampling_rate
    #TODO I could picture this breaking... bc of round
    x_beg = int(round((tr.stats.sac.b*sr)))
    x_end = int(round((tr.stats.sac.e*sr)+1))
    x = range(x_beg,x_end)
    return np.array(x)



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

#def filter_stream_if_has_quality_pick(sac_stream):
#    """ PARKFIELD Returns list, all of events, which have manual picks """ 
#    filtered_stream=[]
#    for trace in sac_stream:
#        try:
#            q = pick_quality(trace,"S")
#            filtered_stream.append(trace)
#        except:
#            pass
#    return filtered_stream


def filter_stream_if_has_sample_rate(streams,sample_rate):
    """ Returns list, all of events, which have manual picks """ 
    filtered_stream=[]
    for trace in streams:
            if trace.stats.delta == sample_rate:
                filtered_stream.append(trace)
    return filtered_stream

def randomly_trim_streams(streams,window_length):
    """ Returns list, all of events, which are larger than desired length
    and cuts them""" 
    filtered_stream=[]
    for trace in streams:
        if len(trace)>window_length:
            starting_pt = random.randint(0,(len(trace)-window_length))
            ##not so random
            starting_pt = 0
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
    binned_data = np.array(zeros(len(s.data)/bin_size))
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
    s = normalize_trace(s,norm_type,1)
    d_pos_list = get_trace_dist_list(s,Rpos,norm_type)
    d_neg_list = get_trace_dist_list(s,Rneg,norm_type)
#   y = .000001
    y = .01
    R = prob_class(d_pos_list,y)/prob_class(d_neg_list,y)

    pos_class = 0
    if R > theta:
        pos_class = 1
    return [R,pos_class]

def shrink(data, rows, cols):
    return data.reshape(rows, data.shape[0]/rows, cols, data.shape[1]/cols).sum(axis=1).sum(axis=2)

def add_spectrogram_data_to_header(trace):
    """ sample rate is hard coded """
    spectrogram_data = cr.spectrogram(trace.data,100) 
    spectrogram_data=shrink(spectrogram_data,8,43)
    trace.stats.update({'spectrogram_data':spectrogram_data})
    

def get_trace_dist_list_spectra(s,ref_set,norm_type):
    """returns a list of distances for the ref_set
    NOT EFFICENT bc calculates spectra each time
    HARD CODED SAMPLE RATE
    """
    s_spec_data = cr.spectrogram(s.data,100)
    s_spec_data=shrink(s_spec_data,8,43)
#    s = normalize_trace(s,norm_type,1)
    dist_list = np.array(zeros(len(ref_set)))
    i = 0
    for r in ref_set:
        r_spec_data = r.stats.spectrogram_data

        D = sum((s_spec_data-r_spec_data)**2)
        qual = get_Spick_quality(r) 
        weight = get_weighted_dist_coefficient(qual)
        dist_list[i] = weight*D
        i = i + 1
    
    return dist_list

def classify_trace(trace,window_length,time_interval,pos_set,neg_set,bin_size,norm_type):
    """Classifies trace by using a sliding time window for a specfied 
    interval and window size."""

    num_of_windows = time_interval[1]- time_interval[0]
    time_window_beg = time_interval[0]
    i=0
    r_list = np.array(zeros(num_of_windows*bin_size))

    while i < num_of_windows:
        #Create window of trace
#        print trace.stats.starttime,trace.stats.endtime
        s = trim_trace(trace,window_length,i+time_window_beg)
#        print s.stats.starttime,s.stats.endtime,s.stats
#        raw_input()
        if i + window_length > len(trace.data):
            break
#           raise Exception(window_length > trace.data)

        [r,pos_signal] = classify_obs(s,pos_set,neg_set,2,10,norm_type)
        for bin_num in range(bin_size):
            r_list[(bin_size*i)+bin_num] = r
        i = i + 1

    return r_list

def get_trace_dist_list(s,ref_set,norm_type):
    """returns a list of distances for the ref_set
    need to look into more"""
#    s = normalize_trace(s,norm_type,1)
    dist_list = np.array(zeros(len(ref_set)))
    i = 0
    for r in ref_set:
        D = sum((s.data-r.data)**2)
#       qual = get_Spick_quality(r) 
#       weight = get_weighted_dist_coefficient(qual)
#       dist_list[i] = weight*D
        dist_list[i] = D
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

def cut_tail_of_longer_list(list1,list2):
    lmin = min(len(list1),len(list2))
    list1 = list1[0:lmin]
    list2 = list2[0:lmin]
    return [list1,list2]

def file_is_in_trace_list(file_name,trace_list):
    for trace in trace_list:
        if trace.stats.file == file_name:
            return True
    return False
