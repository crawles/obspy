from obspy import *
import os

def read_sac_dir(sac_input):
    """ Reads SAC files into directory. Input is a SAC file or directory. 
    Returns a list where each element is a stream, which contains an indivual
    trace
    """
    trace_list = []
    for (dirpath, dirnames, filenames) in os.walk(sac_input):
        for filename in filenames:
            try:
                sac_file = os.path.join(dirpath,filename)
                seismogram = read(sac_file)
                seismogram[0].stats.update({'file':filename})

                trace_list.append(seismogram[0])
            except:
                pass
    return trace_list
