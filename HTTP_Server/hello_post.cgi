#!/usr/bin/python
#Cgi script for a dynamic html form template

import mod_html
import sys
import os

sys.stderr = sys.stdout

def html(method, value):
    print '''\
<!doctype html>
<html>
  <head>
    <title>Say Hello</title>
  </head>
  <body>
    <h1>Hello {0}</h1>
    <h2>Method = {1}</h2>
    <p>
      <form method = "{1}" action = "">
        <p>
          Enter your name:<input type = "text" name = "first" value = "">
        </p>
        <p>
          <input type = "submit" value = "Say Hello">
      </form>
  </body>
</html>
'''.format(value, method)

def main():
    print "Content-type: text/html\n";
    value = ""
    parsed = mod_html.parse()
    if 'first' in parsed:
        value = parsed['first']
    html("GET", value)

main()    


