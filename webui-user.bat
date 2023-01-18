@echo off

set PYTHON=C:\Users\CharlesFettinger\AppData\Local\Programs\Python\Python310\python.exe
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=--gfpgan-model GFPGANv1.4.pth --xformers --no-progressbar-hiding --gradio-img2img-tool color-sketch --skip-torch-cuda-test --disable-safe-unpickle
rem --xformers --precision full --no-half  --medvram
set 'PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256'
set 'OC_CAUSE=1'
rem set ACCELERATE="True"
call webui.bat