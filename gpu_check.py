import torch
import sys

print("Python version:", sys.version)
print("PyTorch version:", torch.__version__)
print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA Device Count:", torch.cuda.device_count())
    print("Current CUDA Device ID:", torch.cuda.current_device())
    print("CUDA Device Name:", torch.cuda.get_device_name(0))
else:
    print("CUDA is NOT available to PyTorch. PyTorch is running on CPU.")
