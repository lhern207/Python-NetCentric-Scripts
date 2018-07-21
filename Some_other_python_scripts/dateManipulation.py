#!/usr/bin/python

"""This program helps visualize how to convert from date string to date object,
   compare two different date objects, differentiate between naive and aware date
   objectsand finally convert from date object to http rfc date string format. 
   This is necessary to implement the conditional get request header"""

from datetime import datetime
import pytz
from os import path

httpdate1 = "Sun, 06 Nov 2015 08:49:37 GMT"
httpdate2 = "Wed, 23 May 2017 08:49:37 GMT"
httpdate3 = "Mon, 07 Nov 2015 08:49:37 GMT"
httpdate4 = "Mon, 07 Nov 2015 14:49:37 GMT"
httpdate5 = "Sun, 06 Nov 1994 08:49:37 GMT"

dateobject1 = datetime.strptime(httpdate1, "%a, %d %b %Y %H:%M:%S %Z")
dateobject2 = datetime.strptime(httpdate2, "%a, %d %b %Y %H:%M:%S %Z")
dateobject3 = datetime.strptime(httpdate3, "%a, %d %b %Y %H:%M:%S %Z")
dateobject4 = datetime.strptime(httpdate4, "%a, %d %b %Y %H:%M:%S %Z")
dateobject5 = datetime.strptime(httpdate5, "%a, %d %b %Y %H:%M:%S %Z")

print "\n"
print "Date 1: " + httpdate1
print "Date 2: " + httpdate2
print "Date 3: " + httpdate3
print "Date 4: " + httpdate4
print "Date 5: " + httpdate5
print "\n"

print "Date 3 older than Date 1: " + str(dateobject3 < dateobject1)
print "Date 3 older than Date 2: " + str(dateobject3 < dateobject2)
print "Date 3 older than Date 4: " + str(dateobject3 < dateobject4)
print "Date 3 older than Date 5: " + str(dateobject3 < dateobject5)

gmt = pytz.timezone("GMT")
dateobject2 = gmt.localize(dateobject2)

seconds = path.getmtime("presentFile.txt")
filedateobject = datetime.fromtimestamp(seconds, pytz.utc)
filedate = datetime.strftime(filedateobject, "%a, %d %b %Y %H:%M:%S %Z")
print "\nFile 'present.txt' was last modified on: " + filedate
print "The file was last modified before Date 3: " + str(filedateobject < dateobject2) + "\n"
