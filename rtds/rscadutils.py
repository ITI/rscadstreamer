import sys
import argparse

import __builtin__


## close up connections and such
def cleanup(rscad, file):
    if rscad is not None:
        rscad.close()

    if file is not None:
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
    parser.add_argument('--plugin-dir', '-p', metavar='PATH', dest='path',
            help='Location of plugins if not in PYTHON_PATH')
    parser.add_argument('--plugin', '-P', action='append',
            metavar='PLUGIN', dest='plugins',
            help='Plugin to load. Multiple --plugin/-P options allowed')
    parser.add_argument('--debug', '-D', action='store_true', dest='debug',
            help='Enable debugging output')
    parser.add_argument('--pid-file', '-r', type=str, dest='pidfile',
            default='/var/run/rscadstreamer.pid', metavar='PIDFILE',
            help='Path to file sotring PID')
    parser.add_argument('--rscad', '-R', metavar='rscad_ip:port',
            type=iptuple, default=None,
            help='IP and Port of RSCAD', dest='rscad')

    # Parse the command line
    args, other_args = parser.parse_known_args()

    ## global for debugging
    __builtin__.__rscaddebug__ = args.debug
    debug('Running in debug mode')

    return args, other_args


def debug(msg):
    if __rscaddebug__:
        print msg
