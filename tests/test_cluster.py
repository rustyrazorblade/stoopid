from uuid import uuid1
from nose.tools import raises
from stoopid.cluster import Cluster, Message, Node, Connection
from mock import patch


# callbacks

class TestMessage(Message):
    id = int

# example of how to test messages and response
def test_register_callback():
    c = Cluster(1234)
    tmp = []

    @c.register(TestMessage)
    def handle_hello(message, connection):
        tmp.append(1)

    c.dispatch(TestMessage(id=1))
    assert tmp == [1]


def test_topology_is_returned():
    c = Cluster(1234)


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


def test_node_context_manager():
    n = Node.create('localhost', 1234)


    with patch.object(Connection, "connect") as m:
        with n.connection as c:
            pass

    assert m.call_count == 1

