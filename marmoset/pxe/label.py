from .client_config import ClientConfig


class Label:
    class Exception(Exception):

        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg


    __instances = []


    @classmethod
    def find(cls, name):
        for i in cls.__instances:
            if name == i.name:
                return i
        raise Exception("No PXELabel with name '%s' found." % (name,))


    @classmethod
    def names(cls):
        """Return the names of all instances of the class."""
        return [x.name for x in cls.__instances]


    def __init__(self, name, callback=None):
        if callback in (None, ''):
            callback=None
        elif not ClientConfig.has_callback(callback):
            msg = "Callback method '%s' doesn't exist. Available: %s"
            callbacklist = ', '.join(ClientConfig.callbacks())
            raise Exception(msg % (callback, callbacklist))

        self.__class__.__instances.append(self)
        self.name = name
        self.callback = callback


