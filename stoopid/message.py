

class Integer(object):
    pytype = int

class MessageMetaClass(type):
    def __new__(meta, name, bases, dct):

        return super(MessageMetaClass, meta).__new__(meta, name, bases, dct)

    def __call__(self, *args, **kwargs):
        pass


class BaseMessage(object):
    __metaclass__ = MessageMetaClass



class Message(BaseMessage):
    # base message class
    pass
