@ECHO OFF
:: Setup batch file to install conda environment
TITLE Setup Conda
ECHO You are about to install the conda environment "mistos", please make sure no environment with the same name exists.
PAUSE
call conda env create -f environment.yml
ECHO Environment Created:
call conda list
call conda activate mistos
call pip install fastai==2.3.1
call pip install napari[all]==0.4.5
call pip install deepflash2==0.1.2
call pip install aiofiles
call pip install czifile
call pip install fastapi
call pip install python-multipart
call pip install simpleitk
call pip install tensorflow==2.4.1
call pip install uvicorn==0.13.4
call pip install auto-tqdm
call pip install sqlalchemy==1.4.0b2
call pip install stardist
call pip install xtiff
call pip install roifile
call pip install pathlib
call pip install python-bioformats==4.0.0
ECHO Create initial config file
python setup.py
PAUSE