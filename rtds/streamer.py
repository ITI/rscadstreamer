
from __future__ import with_statement

import os
import select
import time

## ugh!  Old python


# utility methods
import rtds.rscadutils as util
from rtds.rscadutils import debug

# rscad interaction subsys
import rtds.rscad as rscad

# plugin subsys
from rtds.rscadplugin import PluginMount, RSCADPlugin, loadPlugins


def streamer():
    # Start by loading up available options
    args, other_args = util.parseopts()

    debug('Setting up command channel')
    pid = os.getpid()
    with open(args.pidfile, 'w') as pidfile:
        pidfile.write('{0}'.format(pid))

    cmd_fifo = '/tmp/rscad_streamer_{0}'.format(pid)

    if os.path.exists(cmd_fifo):
        # This shouldn't happen try to rm it
        os.unlink(cmd_fifo)

    os.mkfifo(cmd_fifo)
    cmd_chan = open(cmd_fifo, 'r+')

    # Load up plugins and parse plugin specific command line opts
    debug('loading plugins')
    plugin_args = loadPlugins(args.path, args.plugins, other_args)

    # get an appropriate rscad object
    debug('making rscad obj')
    RSCAD = rscad.rscadfactory(args.rscad, args.ffile)
    debug('RSCAD: %s' % (type(RSCAD)))

    ## Need a (e)poll object - plugins implement input
    # If we're on linux, use epoll's level triggered event interface,
    # it's a fast poll()!
    try:
        poller = select.epoll()
    except AttributeError:
        # Not on linux, use poll()
        try:
            poller = select.poll()
        except:
            # Don't have poll() either? Quit using windows!
            print('Must be run a platform that supports poll() or epoll()')

    # Add the command channel to the poller
    poller.register(cmd_chan.fileno(), select.POLLIN)

    # Init plugins - set up (e)poll for cases that care
    [poller.register(fileno, select.POLLIN) for fileno in [
        p.init(plugin_args) for p in RSCADPlugin.plugins] if
        fileno is not None]

    ## get any plugin commands
    debug('Registering plugin specific commands')
    pcommands = dict()
    [pcommands.update(p.register_commands()) for p in RSCADPlugin.plugins]

    # Need to write rscad script to RSCAD before starting the event loop
    ## Hook up piping
    RSCAD.connect()

    ## main loop
    try:
        debug('starting main loop')
        while True:
            debug('Looping...')
            ## read script file until EOF, pumping it to RSCAD
            rscad_file = RSCAD.makefile()
            while True:
                line = args.script.readline()
                if line == '':
                    # rewind the file for the next pass
                    args.script.seek(0, 0)
                    break
                rscad_file.write(line)
                rscad_file.flush()

            ## Wait for sequence point
            for line in RSCAD.waitforsync('seq1'):
                debug('loop line: %s' % (line))

                [p.handle_output(line) for p in RSCADPlugin.plugins]

            # check for incomming data
            fd = poller.poll(0)

            if fd == cmd_chan.fileno():
                handle_command(fd, pcommands)
            else
                # loop through plugins calling handle_data
                # it's up to the plugin to make sure the data belongs to it
                [[p.handle_input(filedes[0], RSCAD) for p in
                    RSCADPlugin.plugins] for filedes in fd]

            time.sleep(args.sleeptime)

    finally:
        debug('Cleaning up')
        cmd_chan.close()
        os.unlink(cmd_chan.name)
        [p.cleanup() for p in RSCADPlugin.plugins]
        util.cleanup(RSCAD, args.script)


def handle_command(fd, plugin_commands):
    f = fdopen(fd)
    l = f.readlines()

    debug(l)
