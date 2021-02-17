::@ECHO OFF 
:: Simple python http server to serve frontend at port 4200
TITLE Mistos Frontend
ECHO Mistos Frontend serving at port 4200.
cd mistos-frontend/dist/mistos-frontend
conda activate mistos
python server.py
