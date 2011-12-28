from tornado import ioloop

## module local variants of the EVENT types
#   obscureing the event loop for plugin devs
NONE = ioloop.IOLoop.NONE
READ = ioloop.IOLoop.READ
WRITE = ioloop.IOLoop.WRITE
ERROR = ioloop.IOLoop.ERROR


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # we're a mounter
            cls.plugins = list()
        else:
            # we're a plugin
            cls.plugins.append(cls())


class RSCADPlugin(object):
    __metaclass__ = PluginMount

    ## Every plugin should implement options() to define plugin specific
    # command line options.  If none are needed, this will cover it
    def options(self):
        pass

    def register_callback(self, fileno, cb, events):
        l = ioloop.IOLoop.instance()
        l.add_handler(fileno, cb, events)


# Loads the plugins
def loadPlugins(dirs, plugins, opts):
    # get the plugin path from the environment
    evpath = os.environ.get('RSCAD_PLUGIN_PATH', None)
    if evpath is not None:
        envpath = evpath.split(':')
        envpath.reverse()
        # list comprehensions rock!
        [sys.path.insert(0, x) for x in envpath]

    if args.path is not None:
        envpath = dirs.split(':')
        envpath.reverse()
        # list comprehensions rock!
        [sys.path.insert(0, x) for x in envpath]

    if plugins is not None:
        for plug in plugins:
            __import__(plug, globals(), locals(), ['*'], -1)

    # Load any plugin defined command line args, and parse
    plugin_parser = argparse.ArgumentParser()
    [p.options(plugin_parser) for p in RSCADPlugin.plugins]
    return plugin_parser.parse_args(opts)



