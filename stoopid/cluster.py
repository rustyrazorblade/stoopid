import logging
from gevent.server import StreamServer
from message import Message

logger = logging.getLogger(__name__)

class Hello(Message):
    # ask to join cluster
    pass


class Cluster(object):

    informant = None
    informant_port = None


    def __init__(self, informant_port):
        # seed
        assert informant_port > 0
        self.informant_port = informant_port


    def join(self, ip, port):
        logger.info("Joining cluster")
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

    def __init__(self, sock, cluster):
        self.sock = sock
        self.cluster = cluster

    def start(self):
        while True:
            logger.info("sleeping")
            received = self.sock.recv(4096)
            logger.info(received)
