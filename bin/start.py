#!/usr/bin/env python

import sys
sys.path.append("")

import logging
logging.basicConfig(level=logging.INFO)

from stoopid.cluster import Cluster

print "Starting cluster."
c = Cluster()
c.start()

print "Cluster started."


c.run()

print "Done."
