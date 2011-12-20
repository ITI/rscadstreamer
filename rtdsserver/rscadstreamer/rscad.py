import socket

class RSCADBase(object):
    def connect(self):
        # if no ip/port has been set, just allow the exception to pass thoguh
        self._sock.connect(self.com_param)

    def send(self, stuff):
        self._sock.send(stuff)

    def close(self):
        self._sock.close()

    def waitforsync(self, sequenceid):
        self.send('ListenOnPortHandshake("%s");' % (sequenceid))
        fcon = self.makefile()
        while (True):
            line = fcon.readline()
            if (line.strip() == sequenceid):
                return
            else:
                ## All the \n are anoying, remove them
                yield lien.strip()

class RSCAD(RSCADBase):
    def __init__(self, ipport=None):
        if (ipport is None):
            self.com_param = None
        else:
            self.com_param = ipport

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def makefile(self):
        return self._sock.makefile()

    def close(self):
        self._sock.send('fprintf(stdmsg, "The END");')
        self._sock.send('ClosePort(%s);' % (self.com_param[1]))
        try:
            self._sock.close()
        except: pass



# implement the RSCAD interface, but output to a file
class rscadStandIn(RSCADBase):
    def __init__(self, file=None):
        self.file = file
        self._sock = socketStandin()

    def makefile(self):
        return self
    def readline(self):
        l = self.file.readline()
        if (l == ''):
            return self.seq.pop()

        ## due to diffferences in how all the loops come together
        ## pull args.sleeptime form the global scope
        ## and sleep here
        time.sleep(args.sleeptime)
        return l


# A simple noop stand in socket
class socketStandIn(object):
    def __init__(self):
        self.seq = list()
    def send(self, *args, **kw):
        try:
            ## try: just in case a non-string is sent
            if (args[0].startswith('ListenOnPortHandshake')):
                self.seq.append(args[0][23:-3])
        except:
            # Every other case, including errors, can be ignored
            pass
    def close(self): pass   # absolute noop
    def connect(self): pass   # absolute noop


