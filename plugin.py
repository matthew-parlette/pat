class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

class PluginProvider:
    """
    To define a plugin for the system, simply subclass this object.

    The __init__ should be called from your __init__ method, defined as:

        class Plugin(PluginProvider):
            def __init__(self, log, config):
                super(Trello, self).__init__(log, config)
                # Your plugin specific init code goes here

    Plugins should define one of the following, with the specified parameters:

        report

    """
    __metaclass__ = PluginMount

    def __init__(self, log, config):
        log.info("Registering %s as a PluginProvider" % str(self.__class__.__name__))
        self.log = log
        self.config = config

    def report(self,date):
        """Return a string for the report with the filters provided."""
        pass
