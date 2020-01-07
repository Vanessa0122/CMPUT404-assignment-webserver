#  coding: utf-8
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Vanessa Peng
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


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))
        http_method, http_version = self.parse_raw_request(self.data)
        if http_method != 'GET':
            print("405: Method not allowed, only GET is supported by this server.")
        print(http_method, http_version)
        

    # https://github.com/python/cpython/blob/master/Lib/http/server.py#L147, Line 269
    def parse_raw_request(self, raw_request):
        request = str(raw_request, 'utf-8')
        request = request.rstrip('\r\n')
        elements = request.split()
        if len(elements) == 0:
            raise ValueError("Invalid HTTP entry, please  try again")
            
        #Get http_method
        http_method = elements[0]
        #Get http_version
        for i in elements:
            if i.startswith('HTTP/'):
                http_version = i.split('/')[-1]
        return http_method, http_version
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print("Hi")

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
