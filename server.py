#  coding: utf-8
import SocketServer
import os
import mimetypes
import urllib2

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

"""
self.data =
0 GET
1 /index.html
2 HTTP/1.1
3 User-Agent:
4 curl/7.35.0
5 Host:
6 127.0.0.1:8080
7 Accept:
8 */*
"""

class WebPageManager():

    BASE_DIR = "./www"
    path = None

    # Initiliaze the class with usable variables
    def __init__(self, data):
        self.request = data[0]
        self.file    = data[1]
        self.http    = data[2]
        self.address = data[6]
        self.path    = self.BASE_DIR + self.file
        print(self.path)

    # Checks to see if a file exists
    def exists(self):
        if (os.path.exists(self.path) and ".." not in self.path):
            return True
        return False

    def handle(self, server):
        mime_type = mimetypes.guess_type(self.path)[0]
        # If the file has a minetype, serve it
        if (mime_type != None):
            message = self.http + " " + "200 OK\n" + "Content-Type: " + mime_type + "\n\n"
            server.request.sendall(message)
            with open(self.path) as f:
                server.request.sendall(f.read())

        # If no file was specified, return index.html
        elif (mime_type == None):
            self.path = self.path + "/index.html"
            mime_type = mimetypes.guess_type(self.path)[0]
            message = self.http + " " + "200 OK\n" + "Content-Type: " + mime_type + "\n\n"
            server.request.sendall(message)
            with open(self.path) as f:
                server.request.sendall(f.read())

        else:
            server.request.sendall("OK")

    # Returns GET, etc.
    def getRequestType(self):
        return self.request

    # Handles the 404 error
    def notFound(self, server):
        server.request.sendall(self.http + " " + "404 Not found\n\n")
        server.request.sendall("<html lang=en><title>Error 404 Not Found</title>")
        server.request.sendall("<b><body>404 Page not found</body></b>\n\n")



class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        data = self.data.split()
        if (len(data) > 0):
            print ("Got a request of: %s\n" % self.data)
            manager = WebPageManager(data)
            if (manager.getRequestType() == "GET"):
                if (manager.exists()):
                    manager.handle(self)
                else:
                    manager.notFound(self)

        else:
            self.request.sendall("OK")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()