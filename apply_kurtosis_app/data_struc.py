import numpy as np
import swave as sw
import obspy
from collections import defaultdict
import itertools

def Nodes(): return defaultdict(Nodes)

class Dataset:

    def __init__(self,instances):
        self.instances = instances
        self.filenames = self.get_file_names()
        #self.instances_array = self.make_instance_array()

    def __getitem__(self,k):
        return self.instances[k]

    def __len__(self):
        return len(self.instances)

    def make_instance_array(self):
        """ from instances, make 2D array to be used in vectorized k-nearest"""
        instances_array = np.zeros((len(self.instances),len(self.instances[0].data)))
        for i,instance in enumerate(self.instances):
            instances_array[i,:] = instance.data
        return instances_array
    
    @staticmethod
    def normalize_instance_array(instances_array,norm):
        """ Static method so, windowed_data can use """
        c = instances_array
        if norm == 0:
            norm_array = c
            norm_factor = np.amax(np.absolute(norm_array),axis=-1)
        elif norm == 1:
            norm_array = np.absolute(c)
            norm_factor = np.amax(norm_array,axis=-1)
        elif norm == 2:
            norm_array = np.square(c)
            norm_factor = np.amax(norm_array,axis=-1)
        elif norm == 'mpt':
            norm_array = np.absolute(c)
            len_trace = np.shape(norm_array)[-1] 
            norm_factor = np.mean(norm_array[...,0:len_trace/2],axis=-1)
            
        norm_factor_reshape = norm_factor.reshape(np.shape(norm_factor)+(1,))
        return norm_array/norm_factor_reshape

    def get_file_names(self):
        """ need list of file names to for ids, for leave n out """ 
        filenames = []
        for tr in self.instances:
            filenames.append(tr.stats.file)
        return filenames
    
    def contains_filename(self,tr):
        for f in self.filenames:
            if f == tr.stats.file:
                return True
        return False

    def pop_trace(self,pos=0):
        a = self.instances.pop(pos)
        return a

    def append_trace(self,tr):
        self.instances.append(tr)

    def add_R_list(self,R_list):
        """ need instances to have R_list for plotting purposes"""
        for tr,R in zip(self.instances,R_list):
            tr.stats.R = R
    
    def cut_after_S(self,beg,end):
        """ -beg to cut before S """
        for tr in self:
            S = tr.stats.sac.t2 - tr.stats.sac.b
            begS = S + beg
            endS = S + end
            sw.trim_after_start_time(tr,begS,endS)

    def cut_after_P(self,beg,end):
        """ -beg to cut before P """
        for tr in self:
            P = tr.stats.sac.t1 - tr.stats.sac.b
            begP = P + beg
            endP = P + end
            sw.trim_after_start_time(tr,begP,endP)

    def min_S_P(self,t):
        """need to ensure S-P isn't smaller than time window"""
        self.instances[:] = [tr for tr 
                in self 
                if (tr.stats.sac.t2 - tr.stats.sac.t1) >= t
        ]
                #self.instances.remove(tr)
        self.instances_array = self.make_instance_array() # update 2D array


    def mark_picks(self,p):
        for evid in p.picks:
            for trs in sw.pairwise(self):
                tr,tr1=trs[:]
                sta = tr.stats.station
                if tr.stats.file.startswith(evid) and (sta in p.picks[evid]):
                    S_pick = sw.get_relative_time(tr,p.picks[evid][sta])
