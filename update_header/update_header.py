##################################
# Purpose: A directory of sac files needs to be updated because the header
# is out of data for origin time, evla, evlo, and also stla,stlo,cmpinc,cmpaz
#
# # Given a directory of events, 
# outputs a new directory of events 
# with origin time and some picks (t1,t2)
# updated.
#
# tomoDD.reloc must have events in it. you must manually 
# duplicates by printing out and seeing which one closely matches
##################################
import io_utils
import os
import tomoDD
from new_useful_tools import *

#directory which needs to be updated 
old_set = 'targ1_orig/'
##name of directory where new files will be placed
new_dir_name = 'targ1_cte6'

#update locations
tdd = tomoDD.tomoDD('ct_qte6_2013_s.reloc')
#update station header info 
s = tomoDD.Site('wizard.site')

old_set_tr = []
for event in os.listdir(old_set):
    try:
        #############################
        # io_utils.py updates trace #
        #############################
        event_tr = io_utils.read_sac_dir_and_write_new_one(old_set+event,tdd,s,new_dir_name)
    

        old_set_tr = old_set_tr + event_tr
    except Exception,e:
        print str(e)
