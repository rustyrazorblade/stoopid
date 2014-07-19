

class MessageDescriptor(object):

    field = None

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, owner):
        if not instance:
            return
        return instance._values[self.field]

    def __set__(self, instance, value):
        pass



class MessageMetaClass(type):
    def __new__(meta, name, bases, dct):
        attrs = {"_values":{}, "_types": {}}

        for k,v in dct.iteritems():
            if k.startswith("_"):
                attrs[k] = v
                continue

            attrs[k] = MessageDescriptor(k)

            attrs["_values"][k] = None
            attrs["_types"][k] = v

        klass = super(MessageMetaClass, meta).__new__(meta, name, bases, attrs)
        return klass


class BaseMessage(object):
    def __init__(self, **kwargs):
        self._values = kwargs


class Message(BaseMessage):
    # base message class
    __metaclass__ = MessageMetaClass
