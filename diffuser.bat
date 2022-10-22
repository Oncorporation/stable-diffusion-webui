py -m venv ./venv
call ./venv/scripts/activate.bat
pip install diffusers==0.3.0
pip install transformers
pip install onnxruntime
#py -m pip install --upgrade pip

pip install G:\Projects\Stable-Diffusion-webui-amd/ort_nightly_directml-1.13.0.dev20221019004-cp310-cp310-win_amd64.whl --force-reinstall


huggingface-cli.exe login

#convert_stable_diffusion_checkpoint_to_onnx.py --model_path="CompVis/stable-diffusion-v1-5" --output_path="./stable_diffusion_onnx"
