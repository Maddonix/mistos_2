# Mistos
Microscopy Image Storing-and-Processing System

## Voraussetzungen
- Windows
- Anaconda
- Chrome browser (recommended)
- Oracle JDK > 1.6
- microsoft visual c++ 14.0
- Speicherplatz je nach Nutzung
- RAM je nach Größe der zu bearbeitenden Bilder
- (CUDA fähige Grafikkarte für eine bessere Performance)
    - List of Cuda enabled GPU's: https://developer.nvidia.com/cuda-gpus
    - Guide to setup GPU support: https://www.tensorflow.org/install/gpu

## Setup
### Git
- If you already have the latest version of this repository stored locally, skip this section
- If you have not used git before, download and install it
    - https://git-scm.com/downloads
    - Make sure to check "Git from the commandline and also from 3rd party software" option during installation 
- Get latest Mistos build by opening a commandline in a folder where you want to save it
- run "git clone https://github.com/Maddonix/mistos_2.git"

### Oracle JDK
- If already installed (check in system contro -> programs) you may skip this section
- Download and install: 
    - https://www.oracle.com/de/java/technologies/javase-jdk15-downloads.html
    - choose appropriate version (e.g. Windows 64 bit)

### Visual Studio 
- If you already have a Visual C++ Redistributable ( >14.0 ) you may skip this step
- Otherwise visit https://www.microsoft.com/de-de/download/details.aspx?id=48145 , download and install 

### Anaconda
- If you already have an up-to-date version of anaconda installed, you may skip this section (make sure conda is accessable from commandline!)
- Download appropriate Anaconda Version for your system. (Tested with: Windows, Python 3.8, 64-Bit)
    - https://www.anaconda.com/products/individual
- Install Anaconda
    - add conda to path during installation
- Activate conda in the commandline
    - open "anaconda prompt"
    - run "conda init cmd.exe"

### Anaconda Mistos Environment
- Double-click "setup.bat"
    - Warning: Since Mistos implements neuronal networks based on pytorch and tensorflow, both are installed. This takes some time, so you may want to grab a coffee or something to eat in the meantime. 

### Filepaths
- By default, a Mistos directory will be created in your home directory (eg. "c:\\users\\tlux\\mistos")
- Optionally you may change the filepaths:
    - Open the config.json file
    - Enter a valid file path to an existing folder for 
        - "EXPORT_DIRECTORY" (all exports will be stored here)
        - "WORKING_DIRECTORY" (internal storage for the app)

## Start App for the first time:
- for python terminals activate conda: 
-- d:\programming\venv\mistos\scripts\activate.ps1 (powershell)
-- d:\programming\venv\mistos\scripts\activate (regular terminal)

### Frontend
- open a commandline or powershell in "mistos_2" directory
- run "conda activate mistos"
- run "python frontend_server.py"
- allow network access for private networks if requested

### Fileserver
- open a commandline or powershell in "mistos_2/mistos-backend/src" directory
- run "conda activate mistos"
- run "python fileserver/server.py"
- allow network access for private networks if requested

### Backend
- open a commandline or powershell in "mistos_2/mistos-backend/src" directory
- run "conda activate mistos"
- run "python python main.py"
- allow network access for private networks if requested

## Start App After the First Time
 - Double-click "start_mistos.bat"

## Update Environment
- Double-click "update_mistos.bat"

## Troubleshooting
- Anaconda not added to PATH correctly
    - Solution: Add Anaconda to path
        - Find Anaconda path (default is: C:\\users\\{username}\\Anaconda3)
        - Open the Windows menu "Systemumgebungsvariablen bearbeiten" TODO: ADD ENGLISH NAME
        - Go to "Umgebungsvariablen..."
        - double-click on "Path" in the upper list ("Benutzervariablen für {username}")
        - click "New" and paste the Anaconda path
        - click okay and close the menus
        - open the "anaconda prompt"
        - run "conda init cmd.exe"
        - a reboot may be necessary for changes to take effect

- napari errors: 
    - get latest napari build by opening a commandline in a folder where you want to save it
    - run "git clone https://github.com/napari/napari.git"
    - run "cd napari"
    - run "conda activate mistos"
    - run "pip install ."

- Deepflash errors:
    - get forked deepflash2 by opening a commandline in a folder where you want to save it
    - run "git clone https://github.com/Maddonix/deepflash2.git"
    - run "cd deepflash2"
    - run "conda activate mistos"
    - run "pip install -e ."

- You changed the filepaths under config before deleting all entries:
    - The database will still hold references to the old paths, the app will not work anymore
    - Option 1: 
        - change the paths back, the app should work again
        - delete all experiments and images
        - now you may change the path
    - Option 2: 
        - This option will delete all old database references, only do it if you don't need them anymore
        - go to the mistos app folder
        - go to mistos-backend/src
        - delete the file "sql_app.db"

- Conda environment broken:
    - Solution: Rebuild the environment
        - open a commandline in the mistos project folder
        - run "conda remove --name mistos --all"
        - run "conda env create -f environment.yml"


## Main Views:
- Dashboard (default)
- File Viewer
- Experiment Viewer

- Maybe: MachineLearning Screen?

## Processes
### Image Import
1. URL from angular to :7777/api/import_image_series {data: image_path, separate_series: bool = False}
2. calls ie.imported_series_path, series_id = ie.import_file_to_system(importURL, exportURL, separate_series=separate_series)
2. - Reads Metadata
2. - calls db.import_image_series_to_db(filename, n_series) to create db entries, returns name of future image series folder and series id 
2a. - if 


## Functions

## Developer Processes
### Build new frontend distribution
- cd mistos-frontend
- ng build
- git add -f --all :/mistos-frontend/dist
