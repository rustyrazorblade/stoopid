from uuid import uuid1
from nose.tools import raises
from stoopid.cluster import Cluster, Hello, Message, Node



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




def test_node_sets_work():
    tmp = Node.create()
    tmp2 = Node.create()

    nset = set()
    nset.add(tmp)
    nset.add(tmp2)

    assert len(nset) == 2


def test_node_sets_work():
    id = uuid1()

    tmp = Node(id, None, 45)
    tmp2 = Node(id, None, 46)

    nset = set()
    nset.add(tmp)
    nset.add(tmp2)

    assert len(nset) == 1, len(nset)
