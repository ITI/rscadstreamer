
## ugh!  Old python
from __future__ import with_statement

import os
import sys
import select
import time
from io import FileIO


# utility methods
import rtds.rscadutils as util
from rtds.rscadutils import debug

# rscad interaction subsys
import rtds.rscad as rscad

# plugin subsys
#from rtds.rscadplugin import PluginMount, RSCADPlugin, loadPlugins
from rtds.rscadplugin import RSCADPlugin, loadPlugins


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
    cmd_chan = FileIO(cmd_fifo, 'r+')


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
                    try:
                        args.script.seek(0, 0)
                    except IOError:
                        # probably stdin
                        pass
                    break
                rscad_file.write(line)
                rscad_file.flush()

            ## Wait for sequence point
            for line in RSCAD.waitforsync('seq1'):
                debug('loop line: %s' % (line))

                [p.handle_output(line) for p in RSCADPlugin.plugins]

            # check for incomming data
            fd = poller.poll(0)
            debug('Got filedes {0}'.format(fd))

            if cmd_chan.fileno() in [fdes[0] for fdes in fd]:
                handle_command(cmd_chan, pcommands)
            else:
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
        os.unlink(args.pidfile)


def handle_command(cmd_chan, plugin_commands):
    debug('handle_command()')
    l = cmd_chan.read(1000)

    for cmd in l.split('\n'):
        debug('commands: -->{0}<--'.format(cmd))
        if cmd == 'shutdown':
            sys.exit(0)


        ## plugin commands _should_ be in the form of plugin_name:command, but
        #   we'll try to handle the case where a bare command is sent.
        #   We'll assume that any bare command not handled above is meant
        #   for the first plugin that that has a comman component that
        #   matches.

        if cmd in plugin_commands.keys():
            plugin_commands[cmd](cmd)

        else:
            # Ugh!  More LCD crap.  Everything should be 2.7 minimum
            cmds = dict((k.split(':')[1], v) for \
                    (k,v) in plugin_commands.items())

            if cmd in cmds.keys():
                cmds[cmd](cmd)
            else:
                debug('Unhandled command: {0}'.format(cmd))


