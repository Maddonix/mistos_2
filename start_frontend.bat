::@ECHO OFF 
:: Simple python http server to serve frontend at port 4200
TITLE Mistos Frontend
ECHO Mistos Frontend serving at port 4200.
call conda activate mistos
call python frontend_server.py
