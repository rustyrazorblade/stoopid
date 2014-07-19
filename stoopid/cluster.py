import logging
import socket
from gevent.server import StreamServer
from gevent import sleep

logger = logging.getLogger(__name__)

class Cluster(object):

    informant = None


    def __init__(self):
        # seed
        pass

    def join(self, ip, port):
        logger.info("Joining cluster")

    def start(self):
        # starts a cluster, does not join
        logger.info("Starting cluster, not joining")
        self.start_informant()


    def start_informant(self):
        logger.info("Starting informant")

        def handle_connection(socket, address):
            logger.info("Received connection")
            server = InformantServer(socket)
            server.start()

        self.informant = StreamServer(('127.0.0.1', 1234), handle_connection)
        self.informant.serve_forever()


    def run(self):
        pass


class InformantServer(object):
    # serves a single connection
    sock = None
    def __init__(self, sock):
        self.sock = sock

    def start(self):
        while True:
            logger.info("sleeping")
            sleep(1)
