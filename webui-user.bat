@echo off

set PYTHON=C:\Users\CharlesFettinger\AppData\Local\Programs\Python\Python310\python.exe
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--deepdanbooru --api --no-progressbar-hiding --update-check --xformers --gradio-img2img-tool color-sketch --gfpgan-model GFPGANv1.4.pth --skip-torch-cuda-test --precision full --no-half
rem --gfpgan-model GFPGANv1.4.pth
call webui.bat