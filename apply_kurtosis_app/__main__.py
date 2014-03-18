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

#read pick file
pick_file = sys.argv[1]
p = picks.Picks(pick_file)
p.Baillard_2014()

#read raw data
input_sac_directory = sys.argv[2]
obs_set = io_utils.read_sac_dir(input_sac_directory)
#obs_set = sw.update_stream_if_has_quality_pick(obs_set)
#sw.down_sample(obs_set)
obs = data.Dataset(obs_set) 

obs.mark_picks(p)
obs.write_data_to_subdir('updated_data')


