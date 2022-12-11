@echo off

set PYTHON=C:\Users\CharlesFettinger\AppData\Local\Programs\Python\Python310\python.exe
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--gfpgan-model GFPGANv1.4.pth --api --no-progressbar-hiding --xformers --gradio-img2img-tool color-sketch --skip-torch-cuda-test --precision full --no-half
rem --gfpgan-model GFPGANv1.4.pth
call webui.bat