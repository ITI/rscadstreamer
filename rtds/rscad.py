import socket
import pyev
import io
import errno

from rtds.rscadutils import debug


class RSCADNotImplementedException(Exception):
    pass


# factory method that returns the correct rscad source object
def rscadfactory(con_obj, hooks):
    if isinstance(con_obj, tuple):
        debug('Using  RSCADrtds')
        return RSCADrtds(con_obj, hooks)
    elif isinstance(con_obj, str):
        debug('Using  RSCADfile')
        return RSCADfile(con_obj, hooks)
    else:
        debug('Using  RSCADnull')
        return RSCADnull()


## The point of the RSCAD object is to connect to an instance of the
## rscad scriping interface ad marshall script segments and output back and
## forth.



# Required interface for RSCAD obj.  Not strictly necessary,
# more for documentation
class RSCADBase(object):
    def __init__(self, hooks):
        self.sequenceid = None
        self._need_synch = False
        self.indata = None
        self.outdata = None

        self.hooks = hooks

        loop = pyev.default_loop()
        self.watcher = pyev.Io(self._file.fileno(), pyev.EV_READ, loop, self.io)
        self.watcher.start()

    def io(self, watcher, events):
        debug('io({0}, {1}, {2})'.format(type(self),
            type(watcher), type(events)))
        if events & pyev.EV_READ:
            self._handle_read(watcher, events)
        else:
            self._handle_write(watcher, events)

    def send(self, data):
        self.outdata = '{0}{1}'.format(self.outdata, data)
        self.reset(pyev.EV_READ|pyev.EV_WRITE)

    def _handle_read(self, watcher, events):
        debug('_handle_read({0}, {1}, {2})'.format(type(self),
            type(watcher), type(events)))
        debug('Checking for handle_read')
        try:
            debug('Checking for handle_read 2')
            if hasattr(self, 'handle_read'):
                debug('Calling handle_read()')
                self.handle_read(watcher, events)
            else:
                self.indata = self._file.read()
                debug('No class specific read.  Indata is: {0}'.format(
                    self.indata))
        except socket.error, e:
            debug('FUCK!')
            if e.errno == errno.EWOULDBLOCK:
                pass
            else:
                raise
        except Exception, e:
            debug('Unhandled exception: {0}'.format(type(e)))
            raise


        debug('indata is: {0}'.format(self.indata))
        self.indata = self._run_filters(self.indata)
        self._run_hooks('input', self.indata)

        self.indata = None

    def _handle_write(self, watcher, events):
        self._run_hooks('output', self.outdata)

        if hasattr(self, 'handle_write'):
            self.handle_write(watcher, events)
        else:
            self._file.write(self.outdata)

        self.outdata = None
        self.reset(pyev.EV_READ)

    ## Nedd special filter so data can be changed
    def _run_filters(self, data):
        for hook in self.hooks['filters']:
            data = hook(data)
            if data is None:
                break
        return data

    def _run_hooks(self, htype, data):
        for hook in self.hooks[htype]:
            hook(data)

    def reset(self, events):
        self.watcher.stop()
        self.watcher.set(self._file.fileno(), events)
        self.watcher.start()

    def waitforsync(self, sequenceid):
        self.sequenceid = sequenceid
        self.send('ListenOnPortHandshake("{0}");'.format(sequenceid))

class RSCADnull(RSCADBase):
    def __init__(self):
        pass

    def send(self, flags):
        pass

    def waitforsync(self, sequenceid):
        pass


class RSCADrtds(RSCADBase):
    def __init__(self, ipport, hooks):
        self._sock = sockwrap(socket.AF_INET, socket.SOCK_STREAM)
        ## connect, then put into non-blocking
        self._sock.connect(ipport)
        self._sock.setblocking(0)

        self._file = self._sock

        super(RSCADrtds, self).__init__(hooks)


class RSCADfile(RSCADBase):
    def __init__(self, infile, hooks):
        self._file = io.FileIO(infile, "r")
        super(RSCADrtds, self).__init__(hooks)


class sockwrap(socket.socket):
    def read(self, *args):
        d = ''
        while True:
            try:
                d = '{0}{1}'.format(d, self.recv(1024))
                debug('data read: {0}'.format(d))
            except socket.error, e:
                if e.errno == errno.EAGAIN:
                    return d
                else:
                    raise

    def write(self, *args):
        return self.send(args)
