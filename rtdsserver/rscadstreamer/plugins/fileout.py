import sys
from argparse import FileType

from rscadplugin import RSCADPlugin
from rscadutils import iptuple, debug, json_fix

class fileout(RSCADPlugin):
    def options(self, parser):
        parser.add_argument('--fileout-file', required=True,
                dest='fileout_file', type=FileType('w'))

    def init(self, args):
        self.outfile = args.fileout_file

    def handle_output(self, line):
        self.outfile.write(json_fix(line))
