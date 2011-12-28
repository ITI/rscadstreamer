import sys
import argparse

## close up connections and such
def cleanup(rscad, destinations, file):
    rscad.close()

    for d in destinations:
        d.close()

    file.close()


# Make the json ouputted from rscad proper json - tnx Kate
def json_fix(d):
    d = d.replace("'", '"')
    return d + "\n"


# split ip:port tuple into independant elements. Add default port if none gien
def iptuple(ip):
    if (ip is None):
        return None
    r = ip.split(':')
    if (len(r) < 2):
        return (r[0], 5555)
    else:
        return (r[0], int(r[1]))

def parseopts():
    parser = argparse.ArgumentParser(description='RSCAD Script interactions')

    # General options
    parser.add_argument('--delay', '-d', default=0.5, type=float,
            dest='sleeptime', help='how long to sleep between cycles')
    parser.add_argument('--plugin-dir', '-p', metavar='PATH', dest='path',
            help='Location of plugins if not in PYTHON_PATH')
    parser.add_argument('--plugin', '-P', action='append',
            metavar='PLUGIN', dest='plugins',
            help='Plugin to load. Multiple --plugin/-P options allowed')
    parser.add_argument('--script-file', '-f', type=file, default=sys.stdin,
            metavar='FILE', dest='script')

    # Sources (intermediate group for labeled grouping)
    igroup = parser.add_argument_group('Source',
            'Exacly one source must be selected')
    # real group for mutual exclusion
    sgroup = igroup.add_mutually_exclusive_group(required=True)
    sgroup.add_argument('--rscad', '-R', metavar='rscad_ip:port',
            type=iptuple, default=None,
            help='IP and Port of RSCAD', dest='rscad')
    sgroup.add_argument('--from-file', '-F', type=file, default=None,
            metavar='FILE', dest='ffile',
            help='Read data stream from a file generated using --to-file')

    # Parse the command line
    return parser.parse_known_args()
