

class MessageDescriptor(object):
    pass



class MessageMetaClass(type):
    def __new__(meta, name, bases, dct):
        attrs = {}

        for k,v in dct.iteritems():
            if k.startswith("_"): continue

        dct['_attrs'] = attrs

        return super(MessageMetaClass, meta).__new__(meta, name, bases, dct)

    def __call__(self, *args, **kwargs):
        pass


class BaseMessage(object):
    pass



class Message(BaseMessage):
    # base message class
    __metaclass__ = MessageMetaClass
