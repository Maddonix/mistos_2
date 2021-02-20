@ECHO OFF
:: Setup batch file to install conda environment
TITLE Setup Conda
ECHO You are about to install the conda environment "mistos", please make sure no environment with the same name exists.
PAUSE
call conda activate mistos
call conda env update --file environment.yml