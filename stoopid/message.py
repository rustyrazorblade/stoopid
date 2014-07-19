
class MessageException(Exception): pass
class MissingFieldException(MessageException): pass
class ExtraFieldException(MessageException): pass
class TypeException(MessageException): pass

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
    _types = None

    def __init__(self, **kwargs):

        for k in self._types:
            if k not in kwargs:
                raise MissingFieldException("%s is a required field" % k)

        # check for extra fields
        for k in kwargs:
            if k not in self._types:
                raise ExtraFieldException("%s is not part of the spec" % k)

        # check types
        for k, v in kwargs.iteritems():
            if not isinstance(v, self._types[k]):
                raise TypeException()


        self._values = kwargs


class Message(BaseMessage):
    # base message class
    __metaclass__ = MessageMetaClass
