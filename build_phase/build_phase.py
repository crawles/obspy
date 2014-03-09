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

#
sac_data = sys.argv[1]
phase_or_amp = sys.argv[2]

#import all traces
event_list = []
for event in os.listdir(sac_data):
    try:
        event_directory = utils.read_sac_dir(sac_data+"/"+event)
        event_directory = utils.group_stations_for_event(event_directory)
        event_list.append(event_directory)
    except Exception,e:
        print e

#event metadata
tomoDD_src = '/Users/chris/GoogleDrive/fm/current/te2/HASH/te2_longevid.src'
tomoDD_reloc = '/Users/chris/GoogleDrive/fm/current/te2/HASH/te2_qte6_longevid.reloc'
tdd_src = tomoDD.tomoDD(tomoDD_src,tomoDD_reloc)

#build PHASE or AMP
if phase_or_amp == 'phase':
    tdd_src.build_phase(event_list)
elif phase_or_amp == 'amp':
    tdd_src.build_amp(event_list)
else:
    print "not an option"
