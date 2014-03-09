import sac_utils as utils
import swave as sw
import os
import sys
import datetime
import random
from numpy import *
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

first_motion_traces = "bguo2_with_p_phase"
to_be_updated_data = "bguo.picking.target_cliff"
update_data = "bguo3"


all_p_events = []
folder_events = first_motion_traces    
for event in os.listdir(folder_events):
    try:
        event_directory = utils.read_sac_dir(folder_events+"/"+event)
        print len(event_directory)
        all_p_events = all_p_events + event_directory
    except:
        pass

i=0
all_cliff_events = []
folder_events = to_be_updated_data    
for event in os.listdir(folder_events):
    try:
        event_directory = utils.read_sac_dir(folder_events+"/"+event)
        all_cliff_events = all_cliff_events + event_directory

        directory = update_data + "/" + event
        if not os.path.exists(directory):
            os.makedirs(directory)

        for trace in event_directory:
            i = i + 1
            t = utils.find_trace_with_same_file_name(trace,all_p_events)
            #calc offset of two traces
            offset = trace.stats.sac.b - t.stats.sac.b
            trace.stats.sac.a = t.stats.sac.a + offset
            trace.stats.sac.ka = t.stats.sac.ka
            new_file = update_data + "/" + event + "/" + trace.stats.file
            trace.write(new_file, format='SAC')
    except:
        print trace

