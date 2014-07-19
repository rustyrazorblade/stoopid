
from stoopid.message import Message

class TestMessage(Message):
    id = int

def test_message_creation():
    m = TestMessage(id=3)
    assert m
    assert m.id == 3, m.id
