import obspy
def print_header_info(trace):
    for cat in trace.stats:
        print '##'
        if cat =='sac':
            for header in eval('trace.stats.'+cat):
                if not header_val_is_null(eval('trace.stats.'+cat+'.'+header)):
                    print header,'=',eval('trace.stats.'+cat+'.'+header)
        else:
            if not header_val_is_null(eval('trace.stats.'+cat)):
                print cat,'=',eval('trace.stats.'+cat)

def header_val_is_null(header):
    try:
        header = float(header)
    except:
        return False

    if header == -12345.0:
        return True
