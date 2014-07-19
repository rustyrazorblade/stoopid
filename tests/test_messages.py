
from stoopid.message import Message, MessageException, MissingFieldException, ExtraFieldException, TypeException
from nose.tools import raises
from pickle import dumps, loads

class TestMessage(Message):
    id = int

def test_message_creation():
    m = TestMessage(id=3)
    assert m
    assert m.id == 3, m.id


@raises(MissingFieldException)
def test_message_exception_missing_field():
    m = TestMessage()

@raises(ExtraFieldException)
def test_extra_field():
    m = TestMessage(id=2, name="boo")

@raises(TypeException)
def test_wrong_type():
    m = TestMessage(id="wow")


def test_pickle():
    m = TestMessage(id=3)

    pickled = dumps(m)
    m2 = loads(pickled)
    assert m2.id == 3
