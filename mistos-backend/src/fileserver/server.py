import os
from http.server import HTTPServer, CGIHTTPRequestHandler
import pathlib
import json

port = 7778

default_mistos_dir = pathlib.Path.home()
default_fileserver_dir = default_mistos_dir.joinpath("working_directory")
using_default = False

path_cfg = pathlib.Path(pathlib.Path.cwd()).parents[1].joinpath("config.json")
print(path_cfg)
with open(path_cfg, "r") as _file:
    custom_paths = json.load(_file)

# Check for custom fileserver_path
fileserver= pathlib.Path(custom_paths["WORKING_DIRECTORY"])
if fileserver.as_posix() == ".":
    using_default = True
    fileserver = default_fileserver_dir
    print(f"fileserver Directory is: {default_fileserver_dir.as_posix()}")
elif not fileserver.exists():
    using_default = True
    print("WARNING: fileserver path was set to:")
    print(fileserver.as_posix())
    print("Path doesn't exist, using default fileserver directory")
    print(default_fileserver_dir.as_posix())
    using_default = True
    fileserver = default_fileserver_dir
else:
    print("Custom Fileserver Directory:")
    print(fileserver)

os.chdir(fileserver)
print(f"Serving in directory: {os.getcwd()} at port {port}")

server_object = HTTPServer(server_address=('', port), RequestHandlerClass=CGIHTTPRequestHandler)
server_object.serve_forever()