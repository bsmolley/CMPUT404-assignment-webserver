#  coding: utf-8

# Brandon Smolley - Cmput 404
import SocketServer
import os
import mimetypes

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
    CODE_OK  = "200 OK\n"
    CODE_301 = "301 Moved Permanently\r\n"
    CODE_404 = "404 Not found\n\n"
    CONTENT  = "Content-Type: "
    INDEX    = "/index.html"

    # Initiliaze the class with usable variables
    def __init__(self, data):
        self.request = data[0]
        self.file    = data[1]
        self.http    = data[2]
        self.address = data[6]
        self.path    = self.BASE_DIR + self.file
        self.mime_type = mimetypes.guess_type(self.path)[0]
        
    # Checks to see if a file exists
    def exists(self):
        # the ".." check handles any /../../../.. paths
        if (os.path.exists(self.path) and ".." not in self.path):
            return True
        return False

    def handle(self, server):
        # If the file has a mimetype, serve it
        if (self.mime_type != None):
            self.showPage(server)

        # If no file was specified, return index.html
        elif (self.mime_type == None):
            # handles ../deep, as opposed to ../deep/
            if (self.path[-1] != "/"):
                self.redirect(server)
            # normal case, return index.html
            else:
                self.showIndex(server)

        else:
            server.request.sendall("OK")

    # Returns GET, etc.
    def getRequestType(self):
        return self.request

    # Handles the 404 error
    def notFound(self, server):
        server.request.sendall(self.http + " " + self.CODE_404)
        server.request.sendall("<html lang=en><title>Error 404 Not Found</title>")
        server.request.sendall("<b><body>404 Page not found</body></b>\n\n")

    # Handles code 301
    def redirect(self, server):
        message = self.http + " " + self.CODE_301
        server.request.sendall(message)
        server.request.sendall("Location: " + self.file + self.INDEX + "\n\n")
        # server.request.sendall("<html lang=en><title>Error 301 Moved Permanently</title>")
        # server.request.sendall("<b><body>301 Moved Permanently</body></b>\n\n")

    # Handle a case where the page is not specified, returns index.html
    def showIndex(self, server):
        self.path = self.path + self.INDEX
        self.mime_type = mimetypes.guess_type(self.path)[0]
        message = self.http + " " + self.CODE_OK + self.CONTENT + self.mime_type + "\r\n\r\n"
        server.request.sendall(message)
        with open(self.path) as f:
            server.request.sendall(f.read())

    # Normal page request handler, returns desired page
    def showPage(self, server):
        message = self.http + " " + self.CODE_OK + self.CONTENT + self.mime_type + "\n\n"
        server.request.sendall(message)
        with open(self.path) as f:
            server.request.sendall(f.read())


class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        data = self.data.split()
        # only handle valid requests
        if (len(data) > 0):
            print ("Got a request of: %s\n" % self.data)
            # init the WebPageManager with the request information
            manager = WebPageManager(data)
            # if it's a GET request
            if (manager.getRequestType() == "GET"):
                # make sure the file exists
                if (manager.exists()):
                    manager.handle(self)
                # otherwise report a 404 error
                else:
                    manager.notFound(self)

        # safety return
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