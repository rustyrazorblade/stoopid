import logging
from gevent.server import StreamServer
from gevent import socket
from message import Message
from cPickle import dumps, loads
from uuid import UUID, uuid1

logger = logging.getLogger(__name__)

class Hello(Message):
    # ask to join cluster
    node_id = UUID

class Topology(Message):
    nodes = list

class TopologyRequest(Message):
    pass

class NewNodeJoined(Message):
    node_id = UUID

class Node(object):
    node_id = None

    def __init__(self, node_id):
        self.node_id = node_id

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


    def __init__(self, informant_port):
        # seed
        assert informant_port > 0
        self.informant_port = informant_port


    def join(self, ip, port):
        logger.info("Joining cluster")
        conn = Connection.connect(ip, port)
        conn.send(Hello(node_id=uuid1()))
        self.start_informant()

    def start(self):
        # starts a cluster, does not join
        logger.info("Starting cluster, not joining")
        self.start_informant()


    def start_informant(self):
        logger.info("Starting informant")

        def handle_connection(socket, address):
            logger.info("Received connection")
            server = InformantServer(socket, self)
            server.start()

        self.informant = StreamServer(('127.0.0.1', self.informant_port), handle_connection)
        self.informant.serve_forever()


    def run(self):
        pass


class InformantServer(object):
    # serves a single connection
    sock = None
    cluster = None

    def __init__(self, socket, cluster):
        self.conn = Connection(socket)
        self.cluster = cluster

    def start(self):
        while True:
            logger.info("sleeping")
            message = self.conn.recv()
            logger.info(message)
