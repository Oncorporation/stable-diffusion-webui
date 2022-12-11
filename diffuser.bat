#https://rentry.org/ayymd-stable-diffustion-v1_4-guide
py -m venv g://projects//stable-diffusion-webui-nvidia//venv
call  g://projects//stable-diffusion-webui-nvidia//venv/scripts/activate.bat
py .\scripts\pip.exe install diffusers==0.6.0
py .\scripts\pip.exe install transformers
py .\scripts\pip.exe install transformers[onnx]
#py .\scripts\pip.exe install onnxruntime
py .\scripts\pip.exe install onnxruntime-directml
#py -m pip install optimum[onnxruntime]
#py -m pip install --upgrade pip
#py .\scripts\pip.exe install --upgrade pip wheel
#python -m pip install --upgrade pip

pip install g://projects//stable-diffusion-webui-amd//ort_nightly_directml-1.13.0.dev20221021004-cp310-cp310-win_amd64.whl --force-reinstall
# py -m pip install protobuf
# py -m pip install setuptools
#py -m pip install g://projects//stable-diffusion-webui-amd//ort_nightly_directml-1.13.0.dev20221021004-cp310-cp310-win_amd64.whl --force-reinstall
py .\scripts\pip.exe install g://projects//stable-diffusion-webui-nvidia//ort_nightly_directml-1.13.0.dev20221021004-cp310-cp310-win_amd64.whl --force-reinstall

huggingface-cli.exe login hf
#_JJkkYNhUOznFGMfYXoQCdPEgVIlriYVfEG
v14 = "CompVis/stable-diffusion-v1-4"
v15 = "runwayml/stable-diffusion-v1-5"
v15p = "g://projects//stable-diffusion-webui-nvidia//models//Stable-diffusion//v1-5-pruned.ckpt"

v15inpd = "g://projects//stable-diffusion-webui-nvidia//models//Stable-diffusion//sd-v1-5-inpainting.ckpt"
v15inp = "runwayml/stable-diffusion-inpainting"

#convert_stable_diffusion_checkpoint_to_onnx.py --model_path="CompVis/stable-diffusion-v1-4" --output_path="./stable_diffusion_onnx"
#convert_stable_diffusion_checkpoint_to_onnx.py --model_path="CompVis/stable-diffusion-v1-4" --output_path="./onnx"

#G:\Projects\Stable-Diffusion-webui-nvidia\convert_stable_diffusion_checkpoint_to_onnx.py --model_path="runwayml/stable-diffusion-inpainting" --output_path="g://projects//stable-diffusion-webui-nvidia//diffusers//examples//inference/onnx15inpaint"
#G:\Projects\Stable-Diffusion-webui-nvidia\convert_stable_diffusion_checkpoint_to_onnx.py --model_path="g://projects//stable-diffusion-webui-nvidia//models//Stable-diffusion//sd-v1-5-inpainting.ckpt" --output_path="g://projects//stable-diffusion-webui-nvidia//diffusers//examples//inference/onnx15inpaint"