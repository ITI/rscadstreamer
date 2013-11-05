from rtds.rscadplugin import RSCADPlugin
from rtds.rscadutils import debug

import pyev

class autobreak(RSCADPlugin):

    values = [
            {
                'P_GEN1' : '0.54',
                'P_GEN2' : '0.4135',
                'P_GEN3' : '0.4135',
                'P_GEN4' : '0.72',
            },
            {
                'P_GEN1' : '0.61',
            },
            {
                'P_GEN2' : '0.3435',
            },
            {
                'P_GEN1' : '0.75',
            },
        ]





#    values = [
#            {
#                'P_GEN1' : '0.41',   'V_GEN1' : '1.061',
#                'P_GEN2' : '0.8',    'V_GEN2' : '1.051',
#                'P_GEN3' : '0.54',   'V_GEN3' : '1.05077',
#                'P_GEN4' : '0.55',   'V_GEN4' : '1.009',
#            },
#            {
#                'P_GEN1' : '0.54', 'P_GEN2' : '0.4135',
#                'P_GEN3' : '0.0135','P_GEN4' : '0.72'
#            },
#            {'P_GEN1' : '0.61'},
#            {'P_GEN4' : '0.76'},
#            {'P_GEN2' : '0.3435'},
#            {'P_GEN1' : '0.65'},
#            {'P_GEN3' : '0.4'},
#        ]

    def options(self, parser):
        debug('options')

    def init(self, args):

        self.current = 0


        debug('init')

        l = pyev.default_loop()
        self.timer = pyev.Timer(0.0, 30.0, l, self.do_timer)
        self.timer.start()

        return {
            'output': self.do_output,
        }

    def do_output(self, data):
        debug('got: {0}'.format(data))

    def do_timer(self, watcher, events):
        debug('Timer fired')

        print('Setting sequence {0}'.format(self.current))

        rscad = watcher.loop.data

        for k,v in self.values[self.current].items():
            rscad.send('SetSlider "{0}" = {1};'.format(k, v))
        rscad.send('PushButton "SeqTrigger";')
        rscad.send('ReleaseButton "SeqTrigger";')

        if self.current == 0:
            # make sure the breaker are reset
            pyev.sleep(2)
            rscad.send('PushButton "CLOSE";')
            rscad.send('ReleaseButton "CLOSE";')


        if self.current == len(self.values) - 1:
            debug('Resetting timer to 30 seconds')
            watcher.repeat = 60.0
            self.current = 0
        else:
            debug('Leaving timer at 10 seconds')
            watcher.repeat = 30.0
            self.current +=1

        watcher.reset()
