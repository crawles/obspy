import obspy
import io_utils
import swave as sw
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import data_struc as data
import classifier
import plotting as pp
import copy

#observed set
obs_trace_dir = "data/te2_qte6"
obs_set = io_utils.read_sac_dir(obs_trace_dir)

obs_set = sw.update_stream_if_has_quality_pick(obs_set)
sw.down_sample(obs_set)

#import obs dataset, run highpass filter
obspy.Stream(obs_set).filter('highpass', freq=6.0, corners=2, zerophase=True)
obs_set_obj = data.Dataset(obs_set)
obs_set_obj.min_S_P(.71)
#TODO problem with 31,32 when using down_sample
#TODO need to play around with beg time
obs_set_obj.cut_after_P(-.2,10)

#create ref data sets, pos_set and neg_set
pos_set = copy.deepcopy(obs_set)
pos_set_obj = data.Dataset(pos_set)
neg_set = copy.deepcopy(obs_set)
neg_set_obj = data.Dataset(neg_set)

pos_set_obj.cut_after_S(-.5,.5)
neg_set_obj.cut_after_S(1,2)

##test dataset
gamma = .01
n = 4 #leave n out cross validation
beg = 0 #after cut^
end = 10

#classify
test = classifier.Test(obs_set,pos_set,neg_set,gamma)
R_list = test.leave_n_out_cv(n) #classifier
obs_set_obj.add_R_list(R_list)

#metrics
m = classifier.Metrics(obs_set,R_list,beg,end)
#m.dataset_if_error_gt(1)

#pred S arrival
#t = 1.5
#m.trim_around_pred(t)
#m.update_obs_R_set()

#plot
p = pp.Plot(m.obs_set,m.R_set,beg,end)
p.plot_R_list()


#save R
#numpy.savetxt("R_list_mar6.csv", R_list, delimiter=",")
#R_list = np.genfromtxt('R_list.csv', delimiter=',')
