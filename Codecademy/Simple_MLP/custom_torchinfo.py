import time
import torch
import torch.nn as nn

# Optional imports (only used if toggles are enabled)
try:
    from torchviz import make_dot
except ImportError:
    make_dot = None

try:
    from torchview import draw_graph
except ImportError:
    draw_graph = None


def custom_summary(
    model,
    input_size,
    show_graph=False,
    show_architecture=False,
    save_conceptual=False
):
    """
    A Codecademy-style model summary with optional graphical visualizations.

    Parameters:
        model (nn.Module): The PyTorch model to summarize.
        input_size (tuple): Shape of the input tensor.
        show_graph (bool): If True, generate a torchviz computation graph.
        show_architecture (bool): If True, generate a torchview architecture diagram
            using Arial instead of torchview's Linux-specific default font.
        save_conceptual (bool): If True, save the ASCII block diagram to a text file.
    """

    # ------------------------------------------------------------
    # Normalize input_size
    # ------------------------------------------------------------
    if input_size[0] == -1:
        batch_size = 1
        real_input_size = input_size[1:]
    else:
        batch_size = input_size[0]
        real_input_size = input_size[1:]

    x = torch.randn(batch_size, *real_input_size)

    # ------------------------------------------------------------
    # Start timing
    # ------------------------------------------------------------
    summary_start = time.time()
    summary = []

    # ------------------------------------------------------------
    # Hook function
    # ------------------------------------------------------------
    def hook(module, inp, out):
        class_name = module.__class__.__name__
        params = sum(p.numel() for p in module.parameters() if p.requires_grad)
        out_shape = list(out.shape)
        summary.append((class_name, out_shape, params))

    for m in model.modules():
        if not isinstance(m, (nn.Sequential, nn.ModuleList)):
            m.register_forward_hook(hook)

    # ------------------------------------------------------------
    # Forward pass timing
    # ------------------------------------------------------------
    forward_start = time.time()
    y = model(x)
    forward_end = time.time()
    forward_time = forward_end - forward_start

    # ------------------------------------------------------------
    # Print summary table
    # ------------------------------------------------------------
    print("=" * 70)
    print(f"{'Layer (type)':<25}{'Output Shape':<25}{'Param #':<15}")
    print("=" * 70)

    for name, shape, params in summary:
        print(f"{name:<25}{str(shape):<25}{params:<15}")

    total_params = sum(p.numel() for p in model.parameters())
    print("=" * 70)
    print(f"Total params: {total_params}")
    print(f"Trainable params: {total_params}")
    print(f"Non-trainable params: 0")
    print("=" * 70)

    # ------------------------------------------------------------
    # ASCII Block Diagram (DEFAULT)
    # ------------------------------------------------------------
    print("\nModel Block Diagram (ASCII)")
    print("-" * 70)

    block_lines = []
    for name, shape, params in summary:
        line = f"[{name}] -> output {shape} -> params {params}"
        print(line)
        block_lines.append(line)

    print("-" * 70)

    # Save conceptual diagram if requested
    if save_conceptual:
        with open("model_block_diagram.txt", "w") as f:
            for line in block_lines:
                f.write(line + "\n")
        print("Saved conceptual block diagram to model_block_diagram.txt")

    # ------------------------------------------------------------
    # Optional: torchviz computation graph
    # ------------------------------------------------------------
    if show_graph:
        if make_dot is None:
            print("torchviz not installed. Run: pip install torchviz")
        else:
            graph = make_dot(y, params=dict(model.named_parameters()))
            graph.render("model_graph", format="png")
            print("Saved computation graph as model_graph.png")

    # ------------------------------------------------------------
    # Optional: torchview architecture diagram
    # ------------------------------------------------------------
    if show_architecture:
        if draw_graph is None:
            print("torchview not installed. Run: pip install torchview")
        else:
            g = draw_graph(model, input_size=(batch_size, *real_input_size))
            g.visual_graph.node_attr["fontname"] = "Arial"
            g.visual_graph.render("architecture_diagram", format="png")
            print("Saved architecture diagram as architecture_diagram.png")

    # ------------------------------------------------------------
    # Timing results
    # ------------------------------------------------------------
    summary_end = time.time()
    summary_time = summary_end - summary_start

    print(f"\nForward pass time: {forward_time:.6f} seconds")
    print(f"Summary execution time: {summary_time:.6f} seconds")
    print("=" * 70)