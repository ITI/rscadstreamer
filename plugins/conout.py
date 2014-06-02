import sys
from rtds.rscadplugin import RSCADPlugin
from rtds.rscadutils import debug, json_fix

#####################################################
## WARNING!!
## This plugin implements an old plugin API and will not
## function properly with the latest code.
#####################################################

class conout(RSCADPlugin):

    def init(self, args):
        return sys.stdin.fileno()

    def handle_input(self, fileno, rscad):
        if fileno != sys.stdin.fileno():
            # not mine
            return

        data = sys.stdin.readline()
        f = rscad.makefile()

        f.write('Stop;')
        if data == "kick_the_system":
            # hardcoded
            f.write(r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case1\wscc_9bus_demostate1.sib");')
        else:
            # hardcoded
            f.write(r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case2\wscc_9bus_demostate2.sib");')
        f.write('Start;')
        f.flush()

        rscad.waitforsync('console_plugin')

    def handle_output(self, line):
        debug('conout.handle_output()')
        print json_fix(line)
