@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt -q
py manage.py migrate
py manage.py runserver 127.0.0.1:8080
