import build_phase_lib as phase

class tomoDD:

    def __init__(self,tomoDD_file):
        self.tomoDD_file_dict = self.read_tomoDD_file(tomoDD_file)

    def read_tomoDD_file(self,filename):
        tomoDD_f = open(filename,'r')
        event_dict = {}
        sta_dict = {}
        for line in tomoDD_f:
            line_cols = line.split()
            evid = line_cols[0]
            eqlat = line_cols[1]
            eqlon = line_cols[2]
            eqdep = line_cols[3]
            sta = line_cols[4]
            eq_sta_dist = line_cols[8]
            takeoff = line_cols[9]
            azim = line_cols[10]
            sta_dict[sta] = {'eqlat':eqlat,'eqlon':eqlon,'eqdep':eqdep,'eq_sta_dist':eq_sta_dist,'takeoff':takeoff,'azim':azim}
            try:
                event_dict[evid] = dict(event_dict[evid].items() + sta_dict.items())
            except:
                event_dict[evid] = sta_dict
            sta_dict = {}

        return event_dict

    def print_event_header(self,evid):
        sta = self.tomoDD_file_dict[evid].keys()[0]
        dict_item = self.tomoDD_file_dict[evid][sta]
        eqlat = dict_item['eqlat']
        eqlon = dict_item['eqlon']
        eqdep = dict_item['eqdep']
        #iyr,imon,idy,ihr,imn,qsec,qlat,qlon,qdep,qmag,icusp
        #TODO add TIME and magnitude
        return ['0','0','0','0','0','0',eqlat,eqlon,eqdep,'0',evid]

    def flip_polarity(self,sta_name,p):
        """ flip polarity if neccessary """
        #TODO DOUBLE CHECK THIS IS TRUE FOR WIZARD early 2013
        if sta_name in ["COVA","WZ01","WZ02","WZ03","WZ13","WZ14","WZ15","WZ16","WZ17","WZ18","WZ20"]:
            if p == 'D':
                return 'U'
            return 'D'
        else:
            return p

    def build_phase(self,event_list):
        missing_sta = []
        for event in event_list:
            evid = event[0][0].stats.file.split('.')[0]
            #bc tomodd chopped off evid (and i added '201' to beginning)
            if evid in self.tomoDD_file_dict:
                header = self.print_event_header(evid)
                print ' '.join(header)
                for station in event:
                    sta_name = station[0].stats.station
                    if sta_name not in self.tomoDD_file_dict[evid]:
                        missing_sta.append([evid,sta_name])
                    else:
                        td = self.tomoDD_file_dict[evid][sta_name]
                        phase_amp = phase.get_station_phase_and_amp(station)
                        p = phase_amp[0]
                        if p[0]:
                            pass
                            #sname,pickpol,p_qual,qdist,ith,iaz
                            p[0] = self.flip_polarity(sta_name,p[0])
                            print sta_name,p[0],p[1],td['eq_sta_dist'],int(float(td['takeoff'])),int(float(td['azim']))
                print 'NEXT','Q',0,0.0,0,0
        #print missing_sta
    def count_num_of_amp_ratio(self,event):
        i = 0
        evid = event[0][0].stats.file.split('.')[0]
        for station in event:
            sta_name = station[0].stats.station
            if sta_name in self.tomoDD_file_dict[evid]:
                phase_amp = phase.get_station_phase_and_amp(station)
                a = phase_amp[1]
                if a:
                    i = i + 1
        return i

    def build_amp(self,event_list):
        missing_sta = []
        for event in event_list:
            evid = event[0][0].stats.file.split('.')[0]
            #bc tomodd chopped off evid (and i added '201' to beginning)
            orig_evid = evid
            if evid in self.tomoDD_file_dict:
                num_amp = self.count_num_of_amp_ratio(event)
                print evid,num_amp
                for station in event:
                    sta_name = station[0].stats.station
                    if sta_name not in self.tomoDD_file_dict[evid]:
                        missing_sta.append([evid,sta_name])
                    else:
                        td = self.tomoDD_file_dict[evid][sta_name]
                        phase_amp = phase.get_station_phase_and_amp(station)
                        a = phase_amp[1]
                        if a:
                            pass
                            #sname,spin,ith,iaz
                            print sta_name,a,int(float(td['takeoff'])),int(float(td['azim']))
