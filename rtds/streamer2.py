

## ugh!  Old python
from __future__ import with_statement

import os
import sys
import select
import time
from io import FileIO

import pyev


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
    cmd_chan = FileIO(cmd_fifo, 'r+')


    # Load up plugins and parse plugin specific command line opts
    debug('loading plugins')
    plugin_args = loadPlugins(args.path, args.plugins, other_args)

    # get an appropriate rscad object
    #debug('making rscad obj')
    #RSCAD = rscad.rscadfactory(args.rscad, args.ffile)
    #debug('RSCAD: %s' % (type(RSCAD)))

    main_loop = pyev.default_loop()



    # Init plugins - return:
    #   {fileno: n, read_cb: fn, write_cb: fn, commands: {cmd, fn}}
    plugin_commands = {}
    # Add the command channel to the poller

    w = pyev.Io(cmd_chan.fileno(), pyev.EV_READ, main_loop, handle_command,
            data=[plugin_commands, cmd_chan])
    w.start()

    main_loop.start()








def handle_command(watcher, event):
    cmd_chan = watcher.data[1]
    plugin_commands = watcher.data[0]

    debug('handle_command()')
    l = cmd_chan.read(1000)

    for cmd in l.split('\n'):
        debug('commands: -->{0}<--'.format(cmd))
        if cmd == 'shutdown':
            watcher.loop.stop()


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


