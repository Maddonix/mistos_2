# Config
import json
import pathlib

# Read config.json
try:
    path_cfg = pathlib.Path(
        pathlib.Path.cwd()).parents[1].joinpath("config.json")
    with open(path_cfg, "r") as _file:
        settings = json.load(_file)
except:
    path_cfg = pathlib.Path(
        pathlib.Path.cwd()).parents[2].joinpath("config.json")
    with open(path_cfg, "r") as _file:
        settings = json.load(_file)
