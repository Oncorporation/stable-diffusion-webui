@echo off

set PYTHON=C:\Users\CharlesFettinger\AppData\Local\Programs\Python\Python310\python.exe
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--deepdanbooru --skip-torch-cuda-test --no-half --precision full --no-progressbar-hiding --update-check

call webui.bat
