# mistos
Microscopy Image Storing-and-Processing System

## Generate environment
To ensure cross platform compatibility, conda environment was exported using "conda env export --from-history"

## Start App:
- for python terminals activate the venv: 
-- d:\programming\venv\mistos\scripts\activate.ps1 (powershell)
-- d:\programming\venv\mistos\scripts\activate (regular terminal)
- run "ng serve" in "mistos-frontend" directory
- run "python main.py" in "mistos-backend/src"
-- run "uvicorn main:mistos --reload --host 0.0.0.0 --port 7777" in "mistos-backend/src" for debugging
- run "python fileserver.py" in ""mistos-backend/src" 

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