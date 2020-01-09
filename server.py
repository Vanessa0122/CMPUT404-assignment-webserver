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


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        http_method, http_version, host, path = self.parse_raw_request(self.data)
        print(http_method, http_version, host+path)

        if http_method != 'GET':
            request_file_path = "None"
            response = self.build_response(405, request_file_path, host)
            self.request.sendall(response)
        else:
            self.http_request_handler(http_method, http_version, host, path)

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
        #https://stackoverflow.com/users/100297/martijn-pieters
        #https://stackoverflow.com/questions/15115328/python-requests-no-connection-adapters
        for i in range (0, len(elements)-1):
            if elements[i] == "Host:":
                host = "http://" + elements[i+1] #host has to have "http://" in the beginning
        return http_method, http_version, host, path


    def http_request_handler(self, method, http_version, host, path):
        #Path is anything after 127.0.0.1:8080
        #Current directory /Users/mochi/Documents/CMPUT404-assignment-webserver
        request_file_path = os.getcwd()
        if path == '/':
            request_file_path = os.getcwd() + '/www'
        elif path.startswith('/www')!= True and path.endswith('/') != True and os.path.isdir(request_file_path+'/www'+path): #Todo: needs to be imrpoved
            request_file_path = "Null"
            response = self.build_response(303, request_file_path, host)
            self.request.sendall(response)
            return
        else:
            request_file_path = os.getcwd() + '/www' + path
        print(request_file_path)

        if os.path.isfile(request_file_path):
            response = self.build_response(200, request_file_path, host)
        elif os.path.isdir(request_file_path):
            if os.path.isfile(request_file_path+'/index.html'):   #if index.html exists in the directory, return 200
                if request_file_path.endswith('/'):  #if index.html exists in the directory but the path looks like 8080/deep/
                    response = self.build_response(301, request_file_path, host)
                else:
                    response = self.build_response(200, request_file_path, host)
        else:
            response = self.build_response(404, request_file_path, host)
        
        self.request.sendall(response)
        return


    def build_response(self, status_code, path, host):
        response = ""
        if status_code == 200:
            response += "HTTP/1.1 200 OK \n"
            if path.endswith('/'):
                with open(path+"index.html", 'r') as request_file:
                    response_headers = {
                    "Host": host,
                    "Content-Type": self.get_content_type(os.path.splitext(path+"/index.html")[1]), #passing in the extension
                    #"Content-Length": self.get_content_length(path),
                    "Date": datetime.datetime.now()
                    }
                    for key, value in response_headers.items():
                        response += "{}: {}\n".format(key, value)
                    response += request_file.read()

            elif os.path.isfile(path + 'www/index.html'):
                with open(path, 'r') as request_file:
                    response_headers = {
                    "Host": host,
                    "Content-Type": self.get_content_type(os.path.splitext(path)[1]), #passing in the extension
                    #"Content-Length": self.get_content_length(path),
                    "Date": datetime.datetime.now()
                    }
                    for key, value in response_headers.items():
                        response += "{}: {}\n".format(key, value)
                    response += request_file.read()

            elif os.path.isfile(path): #8080/www/deep/index.html or 8080/www/deep/deep.css are existing file
                with open(path, 'r') as request_file:
                    response_headers = {
                    "Host": host,
                    "Content-Type": self.get_content_type(os.path.splitext(path)[1]), #passing in the extension
                    #"Content-Length": self.get_content_length(path),
                    "Date": datetime.datetime.now()
                    }
                    for key, value in response_headers.items():
                        response += "{}: {}\n".format(key, value)
                    response += request_file.read()

            elif os.path.isdir(path):
                with open(path + '/index.html', 'r') as request_file:
                    response_headers = {
                    "Host": host,
                    "Content-Type": self.get_content_type(os.path.splitext(path+'index.html')[1]), #passing in the extension
                    #"Content-Length": self.get_content_length(path),
                    "Date": datetime.datetime.now()
                    }
                    for key, value in response_headers.items():
                        response += "{}: {}\n".format(key, value)
                    response += request_file.read()


        elif status_code == 301:  #Todo: prints with 8080/www/deep/index.html but not 8080/www/deep/
            response += "HTTP/1.1 200 OK\n" #Todo: curl: (18) transfer closed with 291 bytes remaining to read
            path = path[:-1]
            with open(path+"/index.html", 'r') as request_file:
                response_headers = {
                    "Location": host+path,  #Todo: get the new Location
                    "Host": host,
                    "Content-Type": self.get_content_type(os.path.splitext(path+"index.html")[1]), #passing in the extension
                    #"Content-Length": self.get_content_length(path),
                    "Date": datetime.datetime.now()
                }
                for key, value in response_headers.items():
                    response += "{}: {}\n".format(key, value)
                response += request_file.read()

        elif status_code == 303:
            response += "HTTP/1.1 303 See Other\n"

        elif status_code == 404:
            response = "HTTP/1.1 404 Not FOUND!\n"

        elif status_code == 405:
            response = "HTTP/1.1 405 Method Not Allowed \n"
        
        return response.encode()

    def get_content_type(self, extension):
        if extension == ".html":
            return "text/html"
        elif extension == ".css":
            return "text/css"

    def get_content_length(self, path):
        return os.path.getsize(path)

    def prevent_path_traversal(self): #Todo: check file path traversal
        return True


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
