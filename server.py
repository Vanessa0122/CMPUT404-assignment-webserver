#  coding: utf-8
import socketserver
import requests
import os
from urllib import request


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


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        http_method, http_version, host, path = self.parse_raw_request(self.data)
        print(http_method, http_version, host+path)

        #Handle 405 Method Not Allowed first 
        if http_method != 'GET':
            protocol = "HTTP/1.1 405 Method Not Allowed"  
            content = '''<!DOCTYPE html>
                <html>
                    <body>405 Not Found</body>
                </html>
            '''
            header = {"Content-Type": "text/html"}            
            response = self.build_response(header, protocol, content)
            self.request.sendall(response)
            return 
        
        #Handle 200, 301 here 

        request_path = os.getcwd() + '/www' + path    #not supposed to serve http:/127.0.0.1:8080/   http:/127.0.0.1:8080/deep/
        if os.path.isfile(request_path) :
            file_ext = os.path.splitext(request_path)[1]
            print(file_ext)
            if file_ext in ['.css', '.html']:
                protocol = "HTTP/1.1 200 Method OK"
                content = open(request_path).read()
                header={
                    "Host": host,
                    "Content-Type": self.get_content_type(file_ext)
                }
                response = self.build_response(header, protocol, content)
        elif os.path.isdir(request_path):
            if os.path.isfile(request_path+'/index.html'): #if index.html exists in the directory
                if path == '/':
                    protocol = "HTTP/1.1 200 Method OK"
                    content = open(request_path+'/index.html').read()
                    header={
                        "Host": host,
                        "Content-Type": "text/html"
                    }
                    response = self.build_response(header, protocol, content)    
                elif path.endswith('/'):
                    protocol = "HTTP/1.1 200 Method OK"
                    content = open(request_path+'/index.html').read()
                    header={
                        "Host": host,
                        "Content-Type": "text/html"
                    }
                    response = self.build_response(header, protocol, content)
                else:
                    protocol = "HTTP/1.1 301 Moved Permanently"
                    header={
                        "Host": host,
                        "Redirected to": host+path+'/',
                    }
                    response = self.build_response(header, protocol, None)    
                    
        #Left overs are 404 
        else:
            protocol = "HTTP/1.1 404 Not Found"
            content = '''<!DOCTYPE html>
                <html>
                    <body>404 Not Found</body>
                </html>
            '''
            header = {"Content-Type": "text/html"}
            response = self.build_response(header, protocol, content)
        
        self.request.sendall(response)
        return


    # https://github.com/python/cpython/blob/master/Lib/http/server.py#L269
    def parse_raw_request(self, raw_request):
        request = str(raw_request, 'utf-8')
        request = request.rstrip('\r\n')
        elements = request.split()
        if len(elements) == 0:
            raise ValueError("Invalid HTTP entry, please  try again")
        http_method = elements[0]   #Get http_method
        path = elements[1]  #Get path
        for i in elements:
            if i.startswith('HTTP/'):
                http_version = i
        #Get host
        for i in range (0, len(elements)-1):
            if elements[i] == "Host:":
                host = "http://" + elements[i+1] #host has to have "http://" in the beginning
        return http_method, http_version, host, path


    def build_response(self, header, protocol, content):
        complete_message = protocol + '\n'
        for key, value in header.items():
            complete_message += "{}: {}\n".format(key, value) 
        
        #Need to do this otherwise the browser is not going to read the html content!
        complete_message += "\n\n"
        if content != None:
            complete_message += content

        return complete_message.encode()


    def get_content_type(self, extension):
        if extension == ".html":
            return "text/html"
        elif extension == ".css":
            return "text/css"

    #TODO: path traversal 



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
