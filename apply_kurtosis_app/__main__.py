# input: 
#   Baillard_etal_bssa_2014 output file
#   Directory of events

import obspy
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import copy
import io_utils
import swave as sw
import picks 
import data_struc as data
#TODO delete these if you don't end up using them
#import classifier
#import plotting as pp

evid = sys.argv[1]
#read raw data
obs_trace_dir = "data/te2_qte6"
evid_path = os.path.join(obs_trace_dir,evid)
obs_set = io_utils.read_sac_dir(evid_path)
#obs_set = sw.update_stream_if_has_quality_pick(obs_set)
#sw.down_sample(obs_set)
obs = data.Dataset(obs_set) 
#read pick file
p = picks.Picks()
p.add_picks(evid+'.txt',evid)



