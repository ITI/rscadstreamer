

## ugh!  Old python
from __future__ import with_statement

import os
from io import FileIO

import pyev


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

    try:
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

        main_loop = pyev.default_loop()

        # need these, even if empty
        hooks = {
            'plugin_commands': dict(),
            'cleanup' : list(),
            'input' : list(),
            'output' : list(),
            'filters' : list(),
        }

        # Add the command channel to the poller
        w = pyev.Io(cmd_chan.fileno(), pyev.EV_READ, main_loop, handle_command,
                data=[cmd_chan, hooks['plugin_commands']])
        w.start()

        for p in RSCADPlugin.plugins:
            r = p.init(plugin_args)

            # Extract hooks
            if r.has_key('input'):
                hooks['input'].append(r['input'])
            if r.has_key('output'):
                hooks['output'].append(r['output'])
            if r.has_key('commands'):
                hooks['plugin_commands'].update(r['commands'])
            if r.has_key('cleanup'):
                hooks['cleanup'].append(r['cleanup'])
            if r.has_key('filter'):
                hooks['filters'].append(r['filter'])

        ## Setup rscad obj
        debug('making rscad obj')
        RSCAD = rscad.rscadfactory(args.ip, hooks)
        debug('RSCAD type: {0}'.format(type(RSCAD)))

        main_loop.start()

    finally:
        debug('Cleaning up')
        cmd_chan.close()
        os.unlink(cmd_chan.name)
        [cleanup() for cleanup in hooks['cleanup_hooks']]
        #util.cleanup(RSCAD, args.script)
        os.unlink(args.pidfile)


def handle_command(watcher, event):
    cmd_chan = watcher.data[0]
    plugin_commands = watcher.data[1]

    debug('handle_command()')
    l = cmd_chan.read(1000)

    for cmd in l.split('\n'):
        if cmd == '':
            continue
        debug('commands: -->{0}<--'.format(cmd))
        if cmd == 'shutdown':
            watcher.loop.stop()
            return


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


