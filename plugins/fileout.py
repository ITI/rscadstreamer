from argparse import FileType

from rtds.rscadplugin import RSCADPlugin
from rtds.rscadutils import debug

## A basic log to file plugin
class fileout(RSCADPlugin):
    def options(self, parser):
        parser.add_argument('--fileout-file', required=True,
                dest='fileout_file', type=FileType('w'))

    def init(self, args):
        self.outfile = args.fileout_file
        return {
            'input' : self.on_input,
            'cleanup' : self.cleanup,
        }

    def on_input(self, line):
        debug('FILEOUT: got {0}'.format(line))
        self.outfile.write(line)
        self.outfile.flush()

    def cleanup(self):
        self.outfile.close()
