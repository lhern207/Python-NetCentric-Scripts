#!/usr/bin/python
#A program that sets up a condition GET HTTP request for use as telnet input.

import sys
import time

if len(sys.argv) < 4:
    print "Usage: conditionalGet.py host resource value"
    sys.exit()

print "open %s 80" % sys.argv[1]
time.sleep(2)
print "GET %s HTTP/1.1" % sys.argv[2]
print "Host: %s" % sys.argv[1]
print "If-modified-since: %s" % sys.argv[3]
print 
time.sleep(2)
