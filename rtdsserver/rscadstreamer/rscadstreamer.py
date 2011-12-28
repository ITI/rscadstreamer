#!/usr/bin/env python

# stdlib
import sys
import os

# utility methods
import rscadutils as util

# rscad interaction subsys
import rscad

# plugin subsys
from rscadplugin import PluginMount, RSCADPlugin, loadPlugins

# App starts here
if __name__ == '__main__':
    # Start by loading up available options
    args, other_args = util.parseopts()

    # Load up plugins and parse plugin specific command line opts
    plugin_args = loadPlugins(args.path, args.plugins, other_args)

    # get an appropriate rscad object
    RSCAD = rscad.rscadfactory(args.rscad, args.ffile)

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

    # Init plugins - set up (e)poll for cases that care
    [poller.register(fileno, select.POLLIN) for fileno in [
        p.init(plugin_args) for p in RSCADPlugin.plugins] if
        fileno is not None]

    # Need to write rscad script to RSCAD before starting the event loop
    ## Hook up piping
    RSCAD.connect()

    ## main loop
    try:
        while True:
            ## read script file until EOF, pumping it to RSCAD
            rscad_file = RSCAD.makefile()
            while True:
                line = args.file.readline()
                if line == '':
                    # rewind the file for the next pass
                    args.file.seek(0,0)
                    break
                rscad_file.write(line)

            ## Wait for sequence point
            for line in RSCAD.waitforsync('seq1'): pass
                ### output it?

            # check for incomming data
            fd = poller.poll(0)
            # loop through plugins calling handle_data
            # it's up to the plugin to make sure the data belongs to it
            [[p.handle_data(filedes[0], RSCAD) for p in
                RSCADPlugin.plugins] for filedes in fd]

            time.sleep(args.sleeptime)

    finally:
        [p.cleanup() for p in RSCADPlugin.plugins]
        util.cleanup(RSCAD, args.file)
