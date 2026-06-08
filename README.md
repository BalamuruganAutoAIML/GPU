# GPU Utilities for OpenPyXL

## Overview

This repository contains a collection of Python utilities and helper scripts that enable GPU-accelerated processing when working with Excel files using the **openpyxl** library.  The goal is to speed‑up data‑intensive operations (e.g., bulk transformations, large‑scale calculations) by leveraging compatible GPUs via libraries such as **Numba**, **CuPy**, or **PyTorch**.

## Features

- **GPU‑enabled helpers** for reading, writing, and manipulating large worksheets.
- Example scripts demonstrating how to off‑load NumPy‑style calculations to the GPU.
- Helper functions that automatically fall back to CPU when a GPU is not available.
- Clear documentation and type‑hints for easy integration into existing projects.

## Prerequisites

- Python **3.9+**
- `openpyxl` – `pip install openpyxl`
- A compatible GPU driver (CUDA Toolkit 11.0 or newer).
- One of the supported GPU libraries:
  - `cupy` – `pip install cupy-cuda11x`
  - `numba` – `pip install numba`
  - `torch` – `pip install torch` (optional, for deep‑learning workloads)

## Installation

```bash
# Clone the repository
git clone https://github.com/your‑username/gpu‑openpyxl.git
cd gpu‑openpyxl

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> **Note**: The `requirements.txt` file includes `openpyxl` and common GPU libraries. Adjust it based on the library you intend to use.

## Quick Start

```python
import openpyxl
from gpu_utils import gpu_read_excel, gpu_write_excel

# Load an Excel workbook using GPU‑accelerated reading
wb = gpu_read_excel('large_dataset.xlsx')

# Perform a simple GPU‑accelerated operation (example using CuPy)
import cupy as cp
sheet = wb.active
values = cp.array([cell.value for row in sheet.iter_rows() for cell in row], dtype=cp.float32)
# Example: compute the mean on the GPU
mean = cp.mean(values)
print('Mean value (GPU):', mean.get())

# Save the workbook back using GPU‑accelerated writing
gpu_write_excel(wb, 'processed_dataset.xlsx')
```

## Documentation

Detailed API documentation is available in the `docs/` folder and can be generated with Sphinx:

```bash
pip install sphinx
sphinx-build -b html docs/ docs/_build
```

Open `docs/_build/index.html` in your browser to explore the full reference.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b my-feature`).
3. Write tests for your changes.
4. Ensure all existing tests pass: `pytest`.
5. Submit a pull request with a clear description of the changes.

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.

---

*Created on 2026-06-08*
