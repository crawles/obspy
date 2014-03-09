from obspy import *
import os
import sys
import numpy
import datetime
from numpy import *
import copy

#update trace times
def update_trace_header(tr,res,evid,tdd,site):
    #if negative, origin too early
    tr.stats.sac.b =  tr.stats.sac.b + res
    tr.stats.sac.e =  tr.stats.sac.e + res
    tr.stats.sac.t1 =  tr.stats.sac.t1 + res
    tr.stats.sac.t2 =  tr.stats.sac.t2 + res

    #evid lon/lat
    all_event_dict = tdd.all_event_dict
    ev_lat = float(all_event_dict[str(evid)][1])
    ev_lon = float(all_event_dict[str(evid)][2])
#   print evid,":",ev_lat,ev_lon
    tr.stats.sac.evla = ev_lat
    tr.stats.sac.evlo = ev_lon

    #sta lon/lat
    sta = tr.stats.station
    sta_dict = site.site_dict
    sta_lat = float(sta_dict[sta][3])
    sta_lon = float(sta_dict[sta][4])
    tr.stats.sac.stla = sta_lat        
    tr.stats.sac.stlo = sta_lon        

    #cmpinc(ident), cmpaz(imuth)
    component = tr.stats.file.split('.')[-1][-1]
    if component == "E":
        tr.stats.sac.cmpinc = 90
        tr.stats.sac.cmpaz = 90
    elif component == "N":
        tr.stats.sac.cmpinc = 90
        tr.stats.sac.cmpaz = 0
    elif component == "Z":
        pass # don't update

def print_events_with_same_time(tr,tdd,site):
    """ keys with tomoDD.reloc by datetime. must first do a manual check to 
    identify any duplicate events by datetime in tomoDD.reloc and delete all 
    except one """
    print tr.stats.file
    tomoDD_dict = tdd.tomoDD_datetime_dict
    for event in tomoDD_dict:
        # pick new time out from tomoDD catalog
        if abs((tr.stats.starttime - tr.stats.sac.b) - tomoDD_dict[event])<5:
            print "tr:",(tr.stats.starttime -  tr.stats.sac.b),"tomoDD_dict[event]:",tomoDD_dict[event]
            res = (tr.stats.starttime - tr.stats.sac.b) - tomoDD_dict[event]
            print "from tomoDD:", event, "res:",res

def update_trace(tr,tdd,site):
    """ keys with tomoDD.reloc by datetime. must first do a manual check to 
    identify any duplicate events by datetime in tomoDD.reloc and delete all 
    except one """
    tomoDD_dict = tdd.tomoDD_datetime_dict
    for event in tomoDD_dict:
        # pick new time out from tomoDD catalog
        if abs((tr.stats.starttime - tr.stats.sac.b) - tomoDD_dict[event])<5:
            res = (tr.stats.starttime - tr.stats.sac.b) - tomoDD_dict[event]
            update_trace_header(tr,res,event,tdd,site)

def read_sac_dir_and_write_new_one(sac_input,tdd,site,new_dir_name):
    """ Reads SAC files into directory. Input is a SAC file or directory. 
    Returns a list where each element is a stream, which contains an indivual
    trace
    """
    trace_list = []
    if os.path.isdir(sac_input):
        for dirname, dirnames, filenames in os.walk(sac_input):
            for filename in filenames:
                try:
                    sac_file = os.path.join(dirname, filename)
                    seismogram = read(sac_file)
                    seismogram[0].stats.update({'file':filename})

                    ## write new file
                    tr = copy.deepcopy(seismogram[0])
                    print_events_with_same_time(tr,tdd,site)
                    update_trace(tr,tdd,site)
                    new_dir = os.path.join(new_dir_name,filename.split('.')[0])
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    new_file = os.path.join(new_dir,filename)
                    tr.write(new_file,format='SAC')
                    ## 

                    trace_list.append(seismogram[0])
                except Exception,e:
                    print str(e)
            return trace_list
    else:
        seismogram = read(sac_input)
        trace_list.append(seismogram[0])
        return trace_list





