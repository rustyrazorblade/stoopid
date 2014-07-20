from nose.tools import raises
from stoopid.cluster import Cluster, Hello, Message



# callbacks

class TestMessage(Message):
    id = int

def test_register_callback():
    c = Cluster(1234)
    tmp = []

    @c.register(TestMessage)
    def handle_hello(message, connection):
        tmp.append(1)

    c.dispatch(TestMessage(id=1))
    assert tmp == [1]






