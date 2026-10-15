import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.version.cuda)
print(torch.backends.cudnn.version())

print("Is CUDA unlocked? :", torch.cuda.is_available())
print("Target GPU Device Name:", torch.cuda.get_device_name(0))
print("Current CUDA Device ID:", torch.cuda.current_device())
print("CUDA Device Count:", torch.cuda.device_count())
print("Current CUDA Device Name:", torch.cuda.get_device_name(torch.cuda.current_device()))
