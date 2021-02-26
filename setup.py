import json
import pathlib
import os

print("Please enter the input path to the filepath you want to use for Mistos")
print("We will create a folder called 'Mistos' there. It contains your input and output directory")
path = input()

is_dir = False

while is_dir == False:
    path = pathlib.Path(path)
    if path.is_dir():
        is_dir = True
    else:
        print("Path is not valid. Make sure to enter a correct filepath (e.g. 'C:/Users/tlux1/Desktop')")
        path = input()

mistos_path = path.joinpath("Mistos")
export_path = mistos_path.joinpath("export")
fileserver_path = mistos_path.joinpath("fileserver")

os.mkdir(mistos_path)
os.mkdir(export_path)
os.mkdir(fileserver_path)

config = {
    "EXPORT_DIRECTORY": export_path.as_posix(),
    "WORKING_DIRECTORY": fileserver_path.as_posix()
}

with open("config.json", "w") as _file: 
    json.dump(config, _file)

print("Success! Start Mistos by running the 'mistos_start.bat' script.")