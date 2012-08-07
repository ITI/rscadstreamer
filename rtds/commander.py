from __future__ import with_statement

import argparse
import sys

from rscadutils import debug

def commander():
    ## The only options we care about are pid file and command to send
    #   so we'll set up our own option parser

    parser = argparse.ArgumentParser(description='Rscadstreamer commander')
    parser.add_argument('--pid-file', '-p', type=str, dest='pidfile',
            default='/var/run/rscadstreamer.pid', metavar='PIDFILE',
            help='Path to rscadstreamer PID file')

    # Parse the command line
    args, other_args = parser.parse_known_args()

    ## global for debugging
    __builtin__.__rscaddebug__ = args.debug
    debug('Running in debug mode')

    debug('finding PID of streamer')
    with open(args.pidfile) as pidfile:
        pid = pidfile.readline()

    debug('Connecting to streamer at pid {0}',format(pid))
    with open('/tmp/rscad_streamer_{0}'.format(pid), 'a') as cmd_chan:
        debug('sending command {0}'.format(other_args))
        cmd_chan.write(other_args)
        cmd_chan.flush()

