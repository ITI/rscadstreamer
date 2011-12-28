from rscadplugin import RSCADPlugin
from rscadutils import iptuple

class kerk(RSCADPlugin):
    def options(self, parser):
        parser.add_argument('--kerk-remote', '-kr', default=None
                dest='kerk_remote', metavar='ip:port', type=iptuple)

    def init(self, args):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(args.kerk_remote)

        return self.sock.fileno()

    def handle_input(self, fileno, rscad):
        if fileno != self.sock.fileno():
            # not mine
            return

        data = self.sock.recv(1000000)

        rscad.makefile().writeline('Stop;')
        if data == "kick_the_system":
            rscad.makefile().writeline(r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case1\wscc_9bus_demostate1.sib");')
        else:
            rscad.makefile().writeline(r'LoadBatch("C:\RTDS_USER\fileman\KERKdemo\Case1\wscc_9bus_demostate2.sib");')
        rscad.makefile().writeline('Start;')
        rscad.waitforsync('kerk_plugin')

        def handle_output(self, line):
            self.sock.send(line)
