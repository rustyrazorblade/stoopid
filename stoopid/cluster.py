from collections import defaultdict
import logging
from gevent.queue import Queue, Empty
from gevent.server import StreamServer

from gevent import socket
from gevent.pool import Pool
from message import Message
from cPickle import dumps, loads
from uuid import UUID, uuid1

from contextlib import contextmanager

logger = logging.getLogger(__name__)

class NodeJoin(Message):
    # ask to join cluster
    node_id = UUID
    ip = str
    port = int


class Topology(Message):
    # need to allow for more flexible typing, this is list of named tuple
    nodes = list


class TopologyRequest(Message):
    pass


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

    def send(self, message):
        with self.connection as c:
            c.send(message)


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
    _nodes = None # set of Node
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
        @self.register(TopologyRequest)
        def handle_topology_request(message, connection):
            logger.debug("received topology request")
            topology = []
            for node in self._ring._nodes:
                topology.append((node.node_id, node.ip, node.port))
            return topology

        @self.register(NodeJoin)
        def handle_node_join(message, connection):
            logger.info("Node joined %s", message)
            n = Node(message.node_id, message.ip, message.port)

            # if we don't already know about the new node, lets tell everyone
            if n not in self:
                logger.info("node not found in current ring, adding")
                self._ring.add(n)
                logger.info("broadcasting new ring state")
                self.broadcast(message)




    def join(self, ip, port):
        logger.info("Joining cluster")

        conn = Connection.connect(ip, port)

        conn.send(TopologyRequest())
        topology = conn.recv()
        logger.info("got topology response")

        for x in topology:
            self._ring.add(Node(*x))
            print "Added %s:%s:%s to cluster" % (x[0], x[1], x[2])

        logger.info("sending join message for myself")
        conn.send(NodeJoin(node_id=self._node.node_id,
                           ip=self.listen_ip,
                           port=self.informant_port))

        self.start_informant(self.listen_ip)


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

    def broadcast(self, message):
        # tell everyone!
        p = Pool(20)
        tmp = lambda x: x.send(message)
        p.map(tmp, self)


    # iterating over the cluster returns nodes out of the ring
    def __iter__(self):
        for node in self._ring._nodes:
            yield node

    def __contains__(self, node):
        assert isinstance(node, Node)
        return node in self._ring._nodes


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
