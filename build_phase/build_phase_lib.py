#a module to get polarity data and calculate amplitude ratios
#in stream.stats.sac.header
# ka: first motion + quality
# t3,t4: reference point, x_pos of p amplitude
# t5,t6: reference point, x_pos of s amplitude
import numpy as np
import math
def get_station_phase_and_amp(station):
    """ main function, calls functions below """
    #print station[0].stats.file
    station_param = get_station_paramaters(station)
    sta_z=station_param['Z']
    try:
        sta_r=station_param['R']
    except:
        pass
    try:
        sta_t=station_param['T']
    except:
        pass

    if 'ka' not in sta_z:
        phase = [None,None]
    else:
        phase = get_phase_info(sta_z['trace'])

    if len(station) > 2 and get_S_amp(station):
        S_amp = get_S_amp(station)
        P_amp = get_P_amp(station)
        #print 'S_amp =',S_amp,'P_amp =',P_amp
        amp = calc_SP_ratio(P_amp,S_amp)
    else:
        amp = None
    return [phase,amp]

def calc_amp(trace,attribute):
    """ gets y value from x value. input: t3,t4,etc.. """
    sr = trace.stats.sampling_rate
    t_rel = eval("trace.stats.sac." + attribute)
    t_tot = t_rel - trace.stats.sac.b
    x = int((round(sr*t_tot)))
    return trace.data[x]

def calc_p_amp(trace):
    t3_amp = calc_amp(trace,'t3')
    t4_amp = calc_amp(trace,'t4')
    return abs(t4_amp - t3_amp)

def calc_s_amp(trace):
    t5_amp = calc_amp(trace,'t5')
    t6_amp = calc_amp(trace,'t6')
    return abs(t6_amp - t5_amp)

def calc_SP_ratio(cart_sum_p,s_amp):
    ratio = s_amp/cart_sum_p
    return math.log10(ratio)

def get_phase_info(trace):
    """ get ka """
    ka = trace.stats.sac.ka
    pol = ka[2]
    qual = ka[3]
    return [pol,qual]

def header_val_is_null(header):
    try:
        header = float(header)
    except:
        return False

    if header == -12345.0:
        return True
    else:
        return False

def get_station_paramaters(station,rel_params=['ka','t3','t4','t5','t6']):
    """ make dictionary of station paramaters, this is used in main function. 
    parses important info out from headers """
    station_dict = {}
    for trace in station:
        trace_name = trace.stats.file[-1]
        trace_dict = {}
        trace_dict['trace'] = trace
        station_dict[trace_name] = trace_dict

        for p in rel_params:
            header_val = eval('trace.stats.sac.'+p)
            if not header_val_is_null(header_val):
                trace_dict[p] = header_val 
            pass
    return station_dict

def get_S_amp(station):
    sta_par = get_station_paramaters(station)
    for sp in sta_par['R'],sta_par['T']:
        if 't5' in sp and 't6' in sp:
            trace = sp['trace']
            return calc_s_amp(trace)
    return None

def get_P_amp(station):
    sta_par = get_station_paramaters(station)
    p_amp = []

    for sp in sta_par['R'],sta_par['Z']:
        if 't3' in sp and 't4' in sp:
            thresh = 2.0
            if (sp['t4'] - sp['t3']) > thresh:
                print 't4 - t3 >',thresh,'seconds'
            trace = sp['trace']
            trace_amp = calc_p_amp(trace)
            p_amp.append(trace_amp)
    return np.linalg.norm(p_amp)

