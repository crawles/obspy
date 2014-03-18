from obspy import UTCDateTime
class Picks:

    def __init__(self,pick_file):
        self.pick_file = pick_file
        self.Baillard_2014()
        self.sta_picks = self.Baillard_2014()

    def Baillard_2014(self):
        f = open(self.pick_file)
        sta_picks = {}
        for line in f:
            cols = line.split()
            if cols[2] != 'IAML':
                if cols[2][1] == 'S':
                    sta = cols[0]
                    sc = cols[-1]
                    sc_split = sc.split('.')
                    cols[-1] = sc_split[0]
                    cols.append(int(sc_split[1])*10000)
                    time_cols = [int(x) for x in cols[4:]]
                    yr,mn,dy,hr,mn,sc,ms = time_cols[:]
                    t = UTCDateTime(yr,mn,dy,hr,mn,sc,ms) #microseconds
                    sta_picks[cols[0]] = t
        return sta_picks 
