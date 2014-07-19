
from stoopid.message import Message, Integer

class TestMessage(Message):
    id = Integer()

def test_message_creation():
    m = Message(id=3)
