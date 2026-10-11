import time
import torch
import torch.nn as nn
torch.manual_seed(0)

class SimpleMLP(nn.Module):
    def __init__(self, input_size=128, hidden_size=516, output_size=1):
        super().__init__()
        self.fc1   = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2   = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3   = nn.Linear(hidden_size, output_size) 

    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

model = SimpleMLP()

# ----------------------------------------------------------------------
# Custom summary function (replacement for custom_torchinfo)
# ----------------------------------------------------------------------
def custom_summary(model, input_size):
    x = torch.randn(*input_size)
    summary = []
    
    def hook(module, inp, out):
        class_name = module.__class__.__name__
        params = sum(p.numel() for p in module.parameters() if p.requires_grad)
        out_shape = str(list(out.shape))
        summary.append((class_name, out_shape, params))

    for m in model.modules():
        if not isinstance(m, nn.Sequential) and not isinstance(m, nn.ModuleList):
            m.register_forward_hook(hook)

    model(x)

    print("=" * 70)
    print(f"{'Layer (type)':<20}{'Output Shape':<20}{'Param #':<15}")
    print("=" * 70)

    for name, shape, params in summary:
        print(f"{name:<20}{shape:<20}{params:<15}")

    total_params = sum(p.numel() for p in model.parameters())
    print("=" * 70)
    print(f"Total params: {total_params}")
    print(f"Trainable params: {total_params}")
    print(f"Non-trainable params: 0")
    print("=" * 70)

# ----------------------------------------------------------------------
# Run summary
# ----------------------------------------------------------------------
custom_summary(model, input_size=(64, 128))