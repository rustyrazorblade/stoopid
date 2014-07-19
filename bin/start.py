#!/usr/bin/env python

import sys
sys.path.append("")

import argparse
import logging

logging.basicConfig(level=logging.INFO)

from stoopid.cluster import Cluster

parser = argparse.ArgumentParser(description="Stoopid Cluster")
parser.add_argument("-s", dest="seeds", metavar="seeds", nargs="+")
cli = parser.parse_args()

logging.info("Starting cluster.")

c = Cluster()

if not cli.seeds:
    c.start()
else:
    (ip, port) = cli.seeds[0].split(":")
    c.join(ip, port)


logging.info("Cluster started.")


c.run()

logging.info("Done.")
