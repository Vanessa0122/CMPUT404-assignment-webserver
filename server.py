#  coding: utf-8
import socketserver
import requests
import os
import datetime
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

# try: curl -v -X GET http://127.0.0.1:8080/s

root = "www"
class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))
        http_method, http_version, host, path = self.parse_raw_request(self.data)
        if http_method != 'GET':
            status_code = 405
            response_protocol = http_version + " 405 Method Not Allowed"
            self.build_response(status_code, response_protocol, Null, Null)
        else:
            self.http_request_handler(http_method, http_version, host, path)


    # https://github.com/python/cpython/blob/master/Lib/http/server.py#L269
    def parse_raw_request(self, raw_request):
        request = str(raw_request, 'utf-8')
        request = request.rstrip('\r\n')
        elements = request.split()
        if len(elements) == 0:
            raise ValueError("Invalid HTTP entry, please  try again")
        #print(elements)
        http_method = elements[0]   #Get http_method
        path = elements[1]  #Get path
        #Get http_version
        for i in elements:
            if i.startswith('HTTP/'):
                http_version = i
        #Get host
        #https://stackoverflow.com/users/100297/martijn-pieters
        #https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters
        for i in range (0, len(elements)-1):
            if elements[i] == "Host:":
                host = "http://" + elements[i+1] #host has to have "http://" in the beginning

        return http_method, http_version, host, path


    def http_request_handler(self, method, http_version, host, path):
        request_path = root + path #www + /index.html
        request_file_path = os.path.join(os.getcwd(), request_path)
        #Get file extension
        #Author https://stackoverflow.com/users/63485/brian-neal
        #Post https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
        request_file_extension = os.path.splitext(request_file_path)[1]

        if self.file_exists(request_file_path):
            with open(request_file_path, 'r') as request_file:
                status_code = 200
                response_protocol = http_version + " 200 OK"
                response_headers = {
                "Location": host,
                "Content-Type": self.get_content_type(request_file_extension),
                "Content-Length": self.get_content_length(request_file_path),
                "Date": datetime.datetime.now()
                }
            self.build_response(status_code, response_protocol, response_headers, request_file_path)
        else:
            status_code = 404
            response_protocol = http_version + " 404 Not Found"
            self.build_response(status_code, response_protocol, response_headers, Null)

    def build_response(self, status_code, response_protocol, response_headers, request_file_path):
        response = response_protocol + "\n"
        for key, value in response_headers.items():
            #How to print it nicely
            #Author https://stackoverflow.com/users/416500/foslock
            #Post https://stackoverflow.com/questions/44689546/how-to-print-out-a-dictionary-nicely-in-python/44689627
            response += "{}: {}\n".format(key, value)
        if request_file_path:
            response += "\n\n" + open(request_file_path, 'r').read()
        print(response)
        #Http response can't be a string. It needs to be encoded before it is sent
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        return response.encode()

    def get_content_type(self, extension):
        if extension == ".html":
            return "text/html"
        elif extension == ".css":
            return "text/css"

    def get_content_length(self, path):
        body = open(path, 'r').read()
        return len(body)


    def file_exists(self, file_path): #Todo: check file path traversal
        return True


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
