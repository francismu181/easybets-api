@echo off
echo Starting EasyBets API server...
set FLASK_APP=app.py
set FLASK_ENV=development
set DEBUG=true
python -m flask run
