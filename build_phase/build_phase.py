#TODO see if code can get amplitude values even if not in .src
# did you check the polarity function yet to make sure it's updated?
# usage: ipython build_phase.py bguo4
# output: phase file or amp file

import os
import sys
import datetime
import random
from numpy import *
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import build_phase_lib as phase
import tomoDD
import sac_utils as utils

#folder bguo4
alp_events = sys.argv[1]
phase_or_amp = sys.argv[2]

#import all events from bguo4, output event list
event_list = []
for event in os.listdir(alp_events):
    try:
        event_directory = utils.read_sac_dir(alp_events+"/"+event)
        event_directory = utils.group_stations_for_event(event_directory)
        event_list.append(event_directory)
    except Exception,e:
        print e

#output PHASE or AMP
#tomoDD_file = 'feb_27.src' 
tomoDD_file = 'te2.src' 
tdd = tomoDD.tomoDD(tomoDD_file)
if phase_or_amp == 'phase':
    tdd.build_phase(event_list)
elif phase_or_amp == 'amp':
    tdd.build_amp(event_list)

#for event in event_list:
#    print event[0][0].stats.file.split('.')[0][3:-2]
#    for station in event:
#        a = phase.get_station_phase_and_amp(station)
#    #   print station[0].stats.station,a
#    #    print station[0].stats.station,station[0].stats.sac.ka[0:4],'num_stations=',len(station)
#    print ""
