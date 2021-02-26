import os
from http.server import HTTPServer, CGIHTTPRequestHandler
import pathlib

path = pathlib.Path(os.getcwd()).joinpath("mistos-frontend/dist/mistos-frontend")
os.chdir(path)
server_object = HTTPServer(server_address=('', 4200), RequestHandlerClass=CGIHTTPRequestHandler)
server_object.serve_forever()
