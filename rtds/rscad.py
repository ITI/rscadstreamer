import socket
import time

from rtds.rscadutils import debug


class RSCADNotImplementedException(Exception):
    pass


# factory method that returns the correct rscad source object
def rscadfactory(ip, file):
    # Arg parse will only allow ip or file.
    # cannot be both, nor neither
    if ip is not None:
        # Must be real rscad
        return RSCAD(ipport=ip)
    else:
        # Must be replay data
        return rscadStandIn(file=file)


# Required interface for RSCAD obj.  Not strictly necessary,
# more for documentation
# TODO: use ABC (requires python >2.6)
class RSCADBase(object):
    def connect(self, *args, **kw):
        raise RSCADNotImplementedException('connect()')

    def makefile(self, *args, **kw):
        raise RSCADNotImplementedException('makefile()')

    def waitforsync(self, *args, **kw):
        raise RSCADNotImplementedException('waitforsync()')

    def close(self, *args, **kw):
        raise RSCADNotImplementedException('close()')


class RSCAD(RSCADBase):
    def __init__(self, ipport=None):
        if (ipport is None):
            self.com_param = None
        else:
            self.com_param = ipport

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # if no ip/port has been set, just allow the exception to pass thoguh
        self._sock.connect(self.com_param)

    def makefile(self):
        return self._sock.makefile()

    def close(self):
        self._sock.send('fprintf(stdmsg, "The END");')
        self._sock.send('ClosePort(%s);' % (self.com_param[1]))
        try:
            self._sock.close()
        except:
            pass

    def waitforsync(self, sequenceid):
        self._sock.send('ListenOnPortHandshake("%s");' % (sequenceid))
        filecon = self._sock.makefile()
        while True:
            line = filecon.readline()
            debug('incomming line: %s' % (line))
            if (line.strip() == sequenceid):
                return
            else:
                yield line.strip()


# implement the RSCAD interface, but output to a file
class rscadStandIn(RSCADBase):
    def __init__(self, file=None):
        # _sock to remain consistant with RSCAD
        self._file = self._sock = file

    def connect(self):
        # noop as file is passed in already open
        pass

    def makefile(self):
        # Need to intercept (and toss out) writes
        return self

    def write(self, line):
        # another noop (replay ignores "new" input to rscad
        pass

    def flush(self):
        pass

    def close(self):
        if self._file is not None:
            self._file.close()

    def waitforsync(self, sequenceid):
        for line in self._file.readlines():
            # need to throttle data (just in case)
            time.sleep(0.25)
            yield line.strip()
