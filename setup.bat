@ECHO OFF
:: Setup batch file to install conda environment
TITLE Setup Conda
ECHO You are about to install the conda environment "mistos", please make sure no environment with the same name exists.
PAUSE
call conda env create -f environment.yml
call conda activate mistos
call conda install pytorch torchvision torchaudio cpuonly -c pytorch
call conda install -c fastai -c pytorch -c matjesg deepflash2