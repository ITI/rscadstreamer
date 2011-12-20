#!/usr/bin/python

import sys
import argparse

import rscad

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


if __name__ == '__main__':
    # Start by loading up available options
    parser = argparse.ArgumentParser(description='RSCAD Script interactions')

    # General options
    parser.add_argument('--script-file', '-f', type=file, default=sys.stdin,
            help='File containing rscad script')
    parser.add_argument('--delay', '-d', default=0.5, type=float,
            dest='sleeptime', help='how long to sleep between cycles')

    # Sources (intermediate group for labeled grouping)
    igroup = parser.add_argument_group('Source',
            'Exacly one source must be selected')
    # real group for mutual exclusion
    sgroup = igroup.add_mutually_exclusive_group(required=True)
    sgroup.add_argument('--rscad', '-R', metavar='rscad_ip:port', type=iptuple,
            default=None, help='IP and Port of RSCAD', dest='rscad')
    sgroup.add_argument('--from-file', '-F', type=file, default=None,
            metavar='FILE', dest='ffile',
            help='Read data stream from a file generated using --to-file')

    # Destinations
    dgroup = parser.add_argument_group('Destination', 'At least one destination')
    dgroup.add_argument('--dest', '-D', metavar='dest_ip:port', type=iptuple,
            default=None, help='IP and port of destination', dest='dest')
    dgroup.add_argument('--to-file','-t', type=argparse.FileType('a'),
            default=None, metavar='FILE', dest='tfile',
            help='Write data stream to a file for replay')

    # Parse the command line
    args = parser.parse_args()

    # Finally, check that at least one dest was selected (argparse doen't
    # seem to have a built in way to do this
    if ((args.dest is None) and (args.tfile is None)):
        parser.error('Must select at least one destination')


    if (args.rscad is not None):
        rscad = RSCAD(args.rscad)
    else:
        rscad = rscadStandIn(args.ffile)

    rscad.connect()

    destinations = list()
    poller = None

    if (args.send):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(args.send)
        destinations.append(s.makefile())
        ## dest socket can act as a bi-directional com channel, so hook up epoll
        # we're on linux, use epoll's levle triggered event interface,
        # it's a fast poll()!
        try:
            # do it a try block in case someone decided to disable epoll
            # in the kernel (fool)
            poller = select.epoll()
        except AttributeError:
            # Not on linux, use poll
            try:
                poller = select.poll()
            except:
                # Don't have poll() either? Quit using windows!
                print('Must be run a platform that supports poll() or epoll()')
                sys.exit(3)
        ## This is probably very fragile, will have to look into if
        # EPOLLIN and POLLIN are both _always_ 1
        poller.register(s.fileno(), select.POLLIN)

    if (args.tfile is not None):
        destinations.append(args.tfile)


    ## main loop
    try:
        while(True):
            for line in args.file.readlines():
                rscad.send(l)
            # reset file pointer to prep for next pass
            args.file.seek(0)

            # Sync on ListenOnPortHandshake() pumping output from rscad to
            # to dest (not sync notification  from ListenOnPortHandshake())
            for i in rscad.waitforsync('seq2'):
                i_json = json_fix(i)
                for dest in destinations:
                    dest.write('%s\n' % (i_json))

            ## check for incomming data - return immediatly even if no
            #  data available
            if (poller is not None):
                rd = e.poll(0)
                if (len(rd) > 0):
                    ## We only have one socket on the polling interface, and our
                    ##  poll mask only cares about incomming data, so,
                    ##  len(rd) > 0 will only be true if there's something
                    #  we care about
                    handle_incoming(rscad, dest)
            time.sleep(args.sleeptime)

    # Always cleanup (to keep RSCAD from getting in a nasty state)
    finally:
        cleanup(rscad, destintions, args.file)

