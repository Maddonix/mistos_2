@ECHO OFF
:: Setup batch file to install conda environment
TITLE Setup Conda
ECHO You are about to install the conda environment "mistos", please make sure no environment with the same name exists.
PAUSE
call conda env create -f environment.yml
ECHO Environment Created:
call conda list
call conda activate mistos
call pip install fastai
call pip install napari[all]==0.4.5
call pip install deepflash2
call pip install aiofiles
call pip install czifile
call pip install fastapi
call pip install python-multipart
call pip install simpleitk
call pip install tensorflow
call pip install uvicorn
call pip install auto-tqdm
call pip install sqlalchemy==1.4.0b2
call pip install stardist
call pip install xtiff
call pip install roifile
call pip install pathlib
call pip install python-bioformats
ECHO Create initial config file
python setup.py
PAUSE