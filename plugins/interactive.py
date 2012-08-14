import sys
import os
import fcntl

from rtds.rscadplugin import RSCADPlugin
from rtds.rscadutils import debug
from pyev import default_loop, Io, EV_READ

class interactive(RSCADPlugin):
    def init(self, args):
        ## Only works in debug mode
        #if not debug:
        #    return

        debug('INTERACTIVE: init()')

        ## pyev wants FDs to be non-blocking
        #  should we use a dup'd FD here?
#        fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
#        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, fl | os.O_NONBLOCK)
#
#        loop = default_loop()
#        w = Io(sys.stdin.fileno(), EV_READ, loop, self.on_stdin)
#        w.start()

        return {
            'input' : self.on_input,
            'commands': {'interactive:test': self.cmd_test},
        }

    def on_input(self, line):
        print(line.strip())

    def on_stdin(self, watcher, event):
        debug('INTERACTIVE: on_stdin()')
        watcher.stop()
        req = sys.stdin.readlines()
        watcher.data.send('\n'.join(req))
        watcher.start()

    def cmd_test(self, cmd):
        loop = default_loop()
        debug(dir(loop))
