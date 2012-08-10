from argparse import FileType

from rtds.rscadplugin import RSCADPlugin

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
        self.outfile.write(line)
        return line

    def cleanup(self):
        self.outfile.close()
