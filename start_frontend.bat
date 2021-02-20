::@ECHO OFF 
:: Simple python http server to serve frontend at port 4200
TITLE Mistos Frontend
ECHO Mistos Frontend serving at port 4200.
conda activate mistos
python frontend-server.py
