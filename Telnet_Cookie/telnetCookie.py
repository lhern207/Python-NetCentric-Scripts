#!/usr/bin/python
#A program that sets the cookie value for a given
#resource by providing input to telnet.

import sys
import time

if len(sys.argv) < 4:
    print "Usage: tel-cookie.py host resource value"
    sys.exit()

print "open %s 80" % sys.argv[1]
time.sleep(2)
print """\
GET {1} HTTP/1.1
Host: {0}
Cookie: color = "{2}"
""".format(sys.argv[1], sys.argv[2], sys.argv[3])
time.sleep(2)
