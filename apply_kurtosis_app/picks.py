from obspy import UTCDateTime
import data_struc as data

class Picks:

    def __init__(self):
        self.picks = data.Nodes()

    def Baillard_2014(self,pick_file):
        """ input e.g 2012188120908.txt """
        f = open(pick_file)
        sta_picks = data.Nodes()
        for line in f:
            cols = line.split()
            if cols[2] != 'IAML':
                sta = cols[0]
                sc = cols[-1]
                sc_split = sc.split('.')
                cols[-1] = sc_split[0]
                cols.append(int(sc_split[1])*10000)
                time_cols = [int(x) for x in cols[4:]]
                yr,mon,dy,hr,minute,sc,ms = time_cols[:]
                t = UTCDateTime(yr,mon,dy,hr,minute,sc,ms) #microseconds
                sta_picks[cols[0]][cols[2][1]] = t
        return sta_picks 

    def add_picks(self,pick_file,evid):
        """ for evid, add picks """
        self.picks[evid] = self.Baillard_2014(pick_file)
        
