::@ECHO OFF 
:: Simple python http server to serve fileserver at port 7778
TITLE Mistos Fileserver
ECHO Mistos Fileserver booting.
cd mistos-backend/src
call conda activate mistos
call python fileserver/server.py
