@ECHO OFF
:: Setup batch file to install conda environment
TITLE Setup Conda
ECHO You are about to update the conda environment "mistos", please make sure you already installed Mistos (setup.bat).
PAUSE
call conda activate mistos
call conda env update --file environment.yml