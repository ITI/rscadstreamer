#!/usr/bin/python

import socket
import argparse
import sys
import json
import select
import time
from select import epoll

## Quick -n- dirty
class socketStandin(object):
    def __init__(self):
        self.seq=list()
    def send(self, *args, **kw):
        try:
            ## try: just in case a non-string is sent
            if args[0].startswith('ListenOnPortHandshake'):
                self.seq.append(args[0][23:-3])
        except:
            pass
    def close(self): pass

class rscadStandin(socketStandin):
    def __init__(self, file):
        super(rscadStandin, self).__init__()
        self.file = file
    def makefile(self):
        return self
    def readline(self):
        l = self.file.readline()
        if (l == ''):
            return self.seq.pop()

        ## due to diffferences in how all the loops come together
        ## pull args.sleeptime form the global scope
        ## and sleep here
        time.sleep(args.sleeptime)
        return l






def waitforsync(sequenceid, connection):
    print 'waiting for syn: %s' % sequenceid
    connection.send('ListenOnPortHandshake("%s");' % (sequenceid))
    fcon = connection.makefile()
    while (True) :
        line = fcon.readline()
        if (line.strip() == sequenceid):
            return
        else:
            ## All the \n are anoying, remove them
            yield line.strip()

def connect(ipport):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('connecting to %s:%s', ipport)
    sock.connect(ipport)
    print 'connected'
    return sock

def iptuple(ip):
    if (ip is None):
        return None
    r = ip.split(':')
    if (len(r) < 2):
        return (r[0], 5555)
    else:
        return (r[0], int(r[1]))

def cleanup(rscad, rscadport, dest, file):
        rscad.send('fprintf(stdmsg, "The END");')
        rscad.send('ClosePort(%s);' % (rscadport))
        rscad.close()
        dest.close()
        if args.file is not sys.stdin:
            args.file.close()

def make_scriptlet(data):
    ## need to fill this in as details are hashed out.  Here we will
    #   generate a valid rscad scriplet based on an incomming request
    #   This is primarilly intended to implement the start/stop
    #   perterbation functions
    #
    #   for now, just return some arbitraty, but valid rscad
    #   script commands.

    if data == "kick_the_system":
        return ['Stop;',r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case1\wscc_9bus_demostate1.sib");', 'Start;']
    else:
        return ['Stop;',r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case2\wscc_9bus_demostate2.sib");', 'Start;']


def handle_incoming(rscad, dest):
    print 'handle_incoming()'
    # for some reason sock.makefile().readlines() isn't working here
    # no time to figure it out.  Just used sock.recv()
    data = dest.recv(1000000)

    ## make_scriptlet() should return a list of rscad lines that will
    ##  be executed via the sock script interface
    ##
    ##  Warning: The scriptlet output is ignored
    scriplet = make_scriptlet(data)
    print scriplet
    for l in scriplet:
        rscad.send(l)
        ## ...and resync
    for i in waitforsync('scriptlet', rscad): pass

def json_fix(d):
    d = d.replace("'", '"')
    return d + "\n"

if __name__ == '__main__':

    ## Command line options
    parser = argparse.ArgumentParser(description='RSCAD Script interactions')
    parser.add_argument('--rscad', '-R', metavar='rscad_ip:port', type=iptuple,
            default=None, help='IP and Port of RSCAD', dest='rscad')
    parser.add_argument('--dest', '-D', metavar='dest_ip:port', type=iptuple,
            default=None, help='IP and port of destination', dest='dest')
    parser.add_argument('--file', '-f', type=file, default=sys.stdin,
            help='File containing rscad script')
    parser.add_argument('--to-file','-t', type=argparse.FileType('a'),
            default=None, metavar='FILE', dest='tfile',
            help='Write data stream to a file for replay')
    parser.add_argument('--from-file', '-F', type=file, default=None,
            metavar='FILE', dest='ffile',
            help='Read data stream from a file generated using --to-file')
    parser.add_argument('--no-send', '-s', action='store_false', default=True,
            help='Do not send the data to a destination (for writting to file)',
            dest='send')
    parser.add_argument('--delay', '-d', default=0.5, type=float,
            dest='sleeptime', help='how long to sleep between cycles')

    args = parser.parse_args()


    ## Need to validate the cmd line args combination, but we'll do that later


## don't look...
    # Connect to RSCAD
    if (args.rscad is not None):
        rscad = connect(args.rscad)
        for i in waitforsync('seq1', rscad): pass
    else:
        rscad = rscadStandin(args.ffile)

    if (args.send):
        # Connect to dest
        dest = connect(args.dest)
        ## Hook up epoll for incomming commands
        e = epoll()
        e.register(dest.fileno(), select.EPOLLIN)
    else:
        print "Using standin"
        dest = socketStandin()
        e = epoll()


    ##  proxy loop
    try:
        while (True):
            for l in args.file.readlines():
                #rscad.send('%s\n'% (l))
                rscad.send('%s' % (l))
            # Reset file pointer to beginning to prep for next pass
            args.file.seek(0)

            # Sync on ListenOnPortHandshake() pumping output from rscad to
            # to dest (not sync notification  from ListenOnPortHandshake())
            for i in waitforsync('seq2', rscad):
                if (args.tfile is not None):
                    args.tfile.write('%s\n' % (i))
                i_json = json_fix(i)
                dest.sendall(i_json)

            ## check for incomming data - return immediatly even if no
            #   data available
            rd = e.poll(0)
            if (len(rd) > 0):
                ## We only have one socket on the polling interface, and our
                ##  poll mask only cares about incomming data, so,
                ##  len(rd) > 0 will only be true if there's something
                #  we care about
                handle_incoming(rscad, dest)
            time.sleep(args.sleeptime)

    except KeyboardInterrupt:
        cleanup(rscad, args.rscad[1], dest, args.file)
    cleanup(rscad, args.rscad[1], dest, args.file)
