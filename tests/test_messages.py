
from stoopid.message import Message

class TestMessage(Message):
    id = int

def test_message_creation():
    m = Message(id=3)
