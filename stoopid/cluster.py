from collections import defaultdict
import logging
from gevent.queue import Queue, Empty
from gevent.server import StreamServer
from gevent import socket
from message import Message
from cPickle import dumps, loads
from uuid import UUID, uuid1

from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Hello(Message):
    # ask to join cluster
    node_id = UUID
    ip = str
    port = int

class Topology(Message):
    nodes = list

class TopologyRequest(Message):
    pass

class NewNodeJoined(Message):
    node_id = UUID

class Node(object):
    node_id = None
    ip = None
    port = None

    pool = None

    def __init__(self, node_id, ip, port):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.pool = Queue()

    @classmethod
    def create(cls, ip, port):
        return Node(uuid1(), ip, port)

    def __hash__(self):
        return long(self.node_id.hex, 16)

    def __eq__(self, other):
        return self.node_id == other.node_id

    @property
    @contextmanager
    def connection(self):
        # returns a connection
        # to be used as
        # with node.connection as c:
        #     do_stuff_with_c(c)

        try:
            connection = self.pool.get_nowait()
        except Empty:
            connection = Connection.connect(self.ip, self.port)

        yield connection

        self.pool.put(connection)

class Ring(object):
    _nodes = None
    def __init__(self):
        self._nodes = set()

    def add(self, node):
        assert isinstance(node, Node)
        self._nodes.add(node)



class Connection(object):
    sock = None

    def __init__(self, socket):
        self.sock = socket

    @classmethod
    def connect(self, ip, port):
        sock = socket.create_connection((ip, port))
        return Connection(sock)

    def send(self, message):
        pickled = dumps(message)
        self.sock.send(pickled)

    def recv(self):
        # bocks
        pickled = self.sock.recv(4096)
        return loads(pickled)


class Cluster(object):

    informant = None
    informant_port = None

    _event_registry = None
    _ring = None
    _node = None

    # for the informant and client connections
    listen_ip = "127.0.0.1"


    def __init__(self, informant_port):
        # seed
        assert informant_port > 0
        self.informant_port = informant_port
        self._event_registry = defaultdict(set)
        self._ring = Ring()

        # this node has a view of the ring, it's 1 server
        self._node = Node.create(self.listen_ip, informant_port)
        self._ring.add(self._node)

        # this is kind of ugly
        @self.register(Hello)
        def handle_hello(message, connection):
            logger.info("Received hello (%s:%s), added to ring" % (message.ip, message.port))

    def join(self, ip, port):
        logger.info("Joining cluster")

        conn = Connection.connect(ip, port)

        conn.send(Hello(node_id=self._node.node_id,
                        ip=self.listen_ip,
                        port=self.informant_port))

        self.start_informant(self.listen_ip)
        # get ring topology

        # tell everyone about me


    def start(self):
        # starts a cluster, does not join
        logger.info("Starting cluster, not joining")
        self.start_informant(self.listen_ip)


    def start_informant(self, listen_ip):
        logger.info("Starting informant")

        def handle_connection(socket, address):
            logger.info("Received connection")
            server = InformantServer(socket, self)
            server.start()

        self.informant = StreamServer((listen_ip, self.informant_port), handle_connection)
        self.informant.serve_forever()

    def register(self, message_type):
        # registers function which accepts f to be called on event e
        def wrapper(f):
            self._event_registry[message_type].add(f)
            return f
        return wrapper

    def run(self):
        pass

    def dispatch(self, message, connection=None):
        # TODO: support inheritance?
        message_type = type(message)
        for f in self._event_registry[message_type]:
            response = f(message, connection)
            if response:
                connection.send(response)


class InformantServer(object):
    # serves a single connection
    sock = None
    cluster = None
    conn = None

    def __init__(self, socket, cluster):
        self.conn = Connection(socket)
        self.cluster = cluster

    def start(self):
        while True:
            message = self.conn.recv()
            self.cluster.dispatch(message, self.conn)
