import torch
import torch.nn as nn
from collections import OrderedDict

def get_model_summary(model, input_size, device='cpu'):
    """
    Generate a summary of a PyTorch model similar to torchinfo.
    """
    model_was_training = model.training
    model.eval()

    # Remember original device(s)
    try:
        orig_device = next(model.parameters()).device
    except StopIteration:
        orig_device = torch.device('cpu')

    # Move model to requested device
    model = model.to(device)

    summary = OrderedDict()
    hooks = []

    def _shape_of(t):
        if hasattr(t, 'size'):
            return list(t.size())
        return []

    def register_hook(module):
        def hook(module, inp, out):
            class_name = module.__class__.__name__
            module_idx = len(summary)
            m_key = f"{class_name}-{module_idx+1}"

            summary[m_key] = OrderedDict()
            # Inputs/outputs can be tuples; normalize to list of shapes
            in_shapes = []
            if isinstance(inp, (tuple, list)):
                in_shapes = [_shape_of(x) for x in inp]
            else:
                in_shapes = [_shape_of(inp)]
            if len(in_shapes) == 1:
                in_shapes = in_shapes[0]
            summary[m_key]["input_shape"] = in_shapes

            if isinstance(out, (tuple, list)):
                out_shapes = [_shape_of(x) for x in out]
                if len(out_shapes) == 1:
                    out_shapes = out_shapes[0]
            else:
                out_shapes = _shape_of(out)
            summary[m_key]["output_shape"] = out_shapes

            params = 0
            trainable = False
            for p in module.parameters(recurse=False):
                params += p.numel()
                trainable = trainable or p.requires_grad

            if params > 0:
                summary[m_key]["trainable"] = trainable
            summary[m_key]["nb_params"] = params

        # Skip containers only
        if not isinstance(module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
            hooks.append(module.register_forward_hook(hook))

    model.apply(register_hook)

    # Build input on the same device as the model
    x = torch.randn(input_size, device=device) if isinstance(input_size, tuple) else input_size.to(device)

    with torch.no_grad():
        model(x)

    for h in hooks:
        h.remove()

    # Restore model state
    model.to(orig_device)
    if model_was_training:
        model.train()

    return summary

def custom_summary(model, input_size, device='cpu'):
    summary = get_model_summary(model, input_size, device)
    print("=" * 70)
    print(f"{'Layer (type)':>20} {'Output Shape':>25} {'Param #':>15}")
    print("=" * 70)
    total_params = 0
    trainable_params = 0

    for name, layer_info in summary.items():
        out_shape = layer_info['output_shape']
        # Compact pretty-print for list-of-lists from tuple outputs
        out_shape_str = str(out_shape)
        print(f"{name:>20} {out_shape_str:>25} {layer_info['nb_params']:>15,}")
        total_params += layer_info["nb_params"]
        if layer_info.get("trainable", False):
            trainable_params += layer_info["nb_params"]

    print("=" * 70)
    print(f"Total params: {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")
    print(f"Non-trainable params: {total_params - trainable_params:,}")
    print("=" * 70)
