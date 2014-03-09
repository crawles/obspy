import datetime
from obspy import UTCDateTime

class tomoDD:
    """ for reading .reloc NOT .src"""
    def __init__(self,tomoDD_file):
        self.tomoDD_datetime_dict = self.read_tomoDD_file_ymdhs(tomoDD_file)
        self.all_event_dict = self.read_tomoDD_file_all(tomoDD_file)

    def read_tomoDD_file_all(self,file_name):
        tomoDD_f = open(file_name,'r')
        all_event_dict = {}
        for line in tomoDD_f:
            line_cols = line.split()
            all_event_dict[line_cols[0]] = line_cols
        return all_event_dict


    def read_tomoDD_file_ymdhs(self,filename):
        tomoDD_f = open(filename,'r')
        event_dict = {}
        for line in tomoDD_f:
            line_cols = line.split()
            #11
            #2013  1 18  6  9   2372
            evid = int(line_cols[0])
            yr = int(line_cols[10])
            month = int(line_cols[11])
            day = int(line_cols[12])
            hr = int(line_cols[13])
            minute = int(line_cols[14])
            second = line_cols[15].zfill(4)
            t = UTCDateTime(yr,month,day,hr,minute,int(second[:2]),int(second[2:])*10000) #microseconds
            event_dict[evid] = t
        return event_dict

class Site:
    """ wizard.site: contains sta lon/lat """

    def __init__(self,site_file_name):
        self.site_dict = self.make_site_dict(site_file_name)

    def make_site_dict(self,site_file_name):
        site_dict = {}
        site_file = open(site_file_name,'r')
        for line in site_file:
            line_col = line.split()
            site_dict[line_col[0]] = line_col
        return site_dict
        
  

