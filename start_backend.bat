@ECHO OFF 
:: Mistos backend (uvicorn server) @ port 7777
TITLE Mistos Backend
ECHO Mistos Backend serving at port 7777.
cd mistos-backend/src
call conda activate mistos
uvicorn main:mistos --host 0.0.0.0 --port 7777
::python main.py