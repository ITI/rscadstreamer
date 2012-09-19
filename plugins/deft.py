from rtds.rscadplugin import RSCADPlugin
from rtds.rscadutils import debug

class deft(RSCADPlugin):
    def init(self, args):
        debug('DEFT: init()')

        self.sw_state = 0

        return {
            'commands': {'deft:switch': self.cmd_sw_toggle},
        }

    def cmd_sw_toggle(self, cmd, rscad):

        if self.sw_state:
            newstate = 0
        else:
            newstate = 1
        debug('cmd_sw_toggle(): {0} --> {1}'.format(self.sw_state, newstate))
        rscad.send('SetSwitch "Bus9Fault" = {0};'.format(newstate))
        self.sw_state = newstate
