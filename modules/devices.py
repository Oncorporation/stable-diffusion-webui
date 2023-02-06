import sys, os, shlex
import contextlib
from functools import lru_cache

import torch
from modules import errors, shared
from packaging import version


if sys.platform == "darwin":
    from modules import mac_specific

if shared.cmd_opts.use_ipex:
    from modules import xpu_specific


def has_xpu() -> bool:
    return shared.cmd_opts.use_ipex and xpu_specific.has_xpu


def has_mps() -> bool:
    if sys.platform != "darwin":
        return False
    else:
        return mac_specific.has_mps


def get_cuda_device_string():
    from modules import shared

    if shared.cmd_opts.device_id is not None:
        return f"cuda:{shared.cmd_opts.device_id}"

    return "cuda"


def get_optimal_device_name():
    if torch.cuda.is_available():
        return get_cuda_device_string()

    if has_mps():
        return "mps"

    if has_xpu():
        return xpu_specific.get_xpu_device_string()

    return "cpu"


def get_optimal_device():
    return torch.device(get_optimal_device_name())


def get_device_for(task):
    if task in shared.cmd_opts.use_cpu or "all" in shared.cmd_opts.use_cpu:
        return cpu

    return get_optimal_device()


def torch_gc():

    if torch.cuda.is_available():
        with torch.cuda.device(get_cuda_device_string()):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    if has_mps():
        mac_specific.torch_mps_gc()

    if has_xpu():
        xpu_specific.torch_xpu_gc()


def enable_tf32():
    if torch.cuda.is_available():

        # enabling benchmark option seems to enable a range of cards to do fp16 when they otherwise can't
        # see https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/4407
        device_id = (int(shared.cmd_opts.device_id) if shared.cmd_opts.device_id is not None and shared.cmd_opts.device_id.isdigit() else 0) or torch.cuda.current_device()
        if torch.cuda.get_device_capability(device_id) == (7, 5) and torch.cuda.get_device_name(device_id).startswith("NVIDIA GeForce GTX 16"):
            torch.backends.cudnn.benchmark = True

        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True


errors.run(enable_tf32, "Enabling TF32")

cpu: torch.device = torch.device("cpu")
device: torch.device = None
device_interrogate: torch.device = None
device_gfpgan: torch.device = None
device_esrgan: torch.device = None
device_codeformer: torch.device = None
dtype: torch.dtype = torch.float16
dtype_vae: torch.dtype = torch.float16
dtype_unet: torch.dtype = torch.float16
unet_needs_upcast = False


def cond_cast_unet(input):
    return input.to(dtype_unet) if unet_needs_upcast else input


def cond_cast_float(input):
    return input.float() if unet_needs_upcast else input

nv_rng = None
def randn(seed, shape):
    from modules.shared import opts

    torch.manual_seed(seed)
    if opts.randn_source == "CPU" or device.type == 'mps':
        return torch.randn(shape, device=cpu).to(device)
    return torch.randn(shape, device=device)


def randn_without_seed(shape):
    from modules.shared import opts

    if opts.randn_source == "CPU" or device.type == 'mps':
        return torch.randn(shape, device=cpu).to(device)
    return torch.randn(shape, device=device)


def autocast(disable=False):
    from modules import shared

    if disable:
        return contextlib.nullcontext()

    if dtype == torch.float32 or shared.cmd_opts.precision == "full":
        return contextlib.nullcontext()

    return torch.autocast("cuda")


def without_autocast(disable=False):
    return torch.autocast("cuda", enabled=False) if torch.is_autocast_enabled() and not disable else contextlib.nullcontext()


class NansException(Exception):
    pass


def test_for_nans(x, where):
    from modules import shared

    if shared.cmd_opts.disable_nan_check:
        return

    if not torch.all(torch.isnan(x)).item():
        return

    if where == "unet":
        message = "A tensor with all NaNs was produced in Unet."

        if not shared.cmd_opts.no_half:
            message += " This could be either because there's not enough precision to represent the picture, or because your video card does not support half type. Try setting the \"Upcast cross attention layer to float32\" option in Settings > Stable Diffusion or using the --no-half commandline argument to fix this."

    elif where == "vae":
        message = "A tensor with all NaNs was produced in VAE."

        if not shared.cmd_opts.no_half and not shared.cmd_opts.no_half_vae:
            message += " This could be because there's not enough precision to represent the picture. Try adding --no-half-vae commandline argument to fix this."
    else:
        message = "A tensor with all NaNs was produced."

    message += " Use --disable-nan-check commandline argument to disable this check."
    raise NansException(message)

# MPS workaround for https://github.com/pytorch/pytorch/issues/79383
orig_tensor_to = torch.Tensor.to
def tensor_to_fix(self, *args, **kwargs):
    if self.device.type != 'mps' and \
       ((len(args) > 0 and isinstance(args[0], torch.device) and args[0].type == 'mps') or \
       (isinstance(kwargs.get('device'), torch.device) and kwargs['device'].type == 'mps')):
        self = self.contiguous()
    return orig_tensor_to(self, *args, **kwargs)


# MPS workaround for https://github.com/pytorch/pytorch/issues/80800 
orig_layer_norm = torch.nn.functional.layer_norm
def layer_norm_fix(*args, **kwargs):
    if len(args) > 0 and isinstance(args[0], torch.Tensor) and args[0].device.type == 'mps':
        args = list(args)
        args[0] = args[0].contiguous()
    return orig_layer_norm(*args, **kwargs)


# MPS workaround for https://github.com/pytorch/pytorch/issues/90532
orig_tensor_numpy = torch.Tensor.numpy
def numpy_fix(self, *args, **kwargs):
    if self.requires_grad:
        self = self.detach()
    return orig_tensor_numpy(self, *args, **kwargs)


# MPS workaround for https://github.com/pytorch/pytorch/issues/89784
orig_cumsum = torch.cumsum
orig_Tensor_cumsum = torch.Tensor.cumsum
def cumsum_fix(input, cumsum_func, *args, **kwargs):
    if input.device.type == 'mps':
        output_dtype = kwargs.get('dtype', input.dtype)
        if output_dtype == torch.int64:
            return cumsum_func(input.cpu(), *args, **kwargs).to(input.device)
        elif cumsum_needs_bool_fix and output_dtype == torch.bool or cumsum_needs_int_fix and (output_dtype == torch.int8 or output_dtype == torch.int16):
            return cumsum_func(input.to(torch.int32), *args, **kwargs).to(torch.int64)
    return cumsum_func(input, *args, **kwargs)


if has_mps():
    if version.parse(torch.__version__) < version.parse("1.13"):
        # PyTorch 1.13 doesn't need these fixes but unfortunately is slower and has regressions that prevent training from working
        torch.Tensor.to = tensor_to_fix
        torch.nn.functional.layer_norm = layer_norm_fix
        torch.Tensor.numpy = numpy_fix
    elif version.parse(torch.__version__) > version.parse("1.13.1"):
        cumsum_needs_int_fix = not torch.Tensor([1,2]).to(torch.device("mps")).equal(torch.ShortTensor([1,1]).to(torch.device("mps")).cumsum(0))
        cumsum_needs_bool_fix = not torch.BoolTensor([True,True]).to(device=torch.device("mps"), dtype=torch.int64).equal(torch.BoolTensor([True,False]).to(torch.device("mps")).cumsum(0))
        torch.cumsum = lambda input, *args, **kwargs: ( cumsum_fix(input, orig_cumsum, *args, **kwargs) )
        torch.Tensor.cumsum = lambda self, *args, **kwargs: ( cumsum_fix(self, orig_Tensor_cumsum, *args, **kwargs) )
        orig_narrow = torch.narrow
        torch.narrow = lambda *args, **kwargs: ( orig_narrow(*args, **kwargs).clone() )

    x = torch.zeros((1, 1, 3, 3)).to(device, dtype)
    conv2d = torch.nn.Conv2d(1, 1, (3, 3)).to(device, dtype)
    conv2d(x)

