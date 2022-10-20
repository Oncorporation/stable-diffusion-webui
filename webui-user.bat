@echo off

set PYTHON=C:\Users\CharlesFettinger\AppData\Local\Programs\Python\Python310\python.exe
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--deepdanbooru --skip-torch-cuda-test --precision full --no-half --no-progressbar-hiding --update-check --gradio-img2img-tool color-sketch

call webui.bat
