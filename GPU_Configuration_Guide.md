# Comprehensive GPU Configuration Guide for PyTorch & CUDA

This document provides a complete, step-by-step guide to configuring and using your NVIDIA GPU for deep learning and GPU-accelerated computing with Python and PyTorch. 

---

## 🔍 Your System Status (Auto-Detected)

We executed your `gpu_check.py` script using your custom Python environment. The good news is **your GPU is already successfully configured and fully accessible to PyTorch!**

Here are the details of your active configuration:

| Component | Detected Value | Status |
| :--- | :--- | :--- |
| **Python Path** | `C:\Python\Bala\Scripts\python.exe` | Active Environment |
| **Python Version** | `3.14.4` | Verified |
| **PyTorch Version** | `2.11.0+cu126` | Verified (CUDA 12.6 Build) |
| **CUDA Available** | `True` | **Successful** 🚀 |
| **GPU Model** | **NVIDIA GeForce GTX 1650** | Connected & Active |
| **CUDA Device ID** | `0` | Default Device |

---

## 🛠️ Step-by-Step GPU Configuration Guide

If you ever need to set up a new environment, upgrade your system, or configure a new machine, follow this complete step-by-step workflow:

### Step 1: Verify Hardware & Install NVIDIA Drivers
To use CUDA, you must have an NVIDIA GPU. 
1. **Check GPU:** Open Windows **Task Manager** (Ctrl+Shift+Esc), go to the **Performance** tab, and select **GPU** to confirm you have an NVIDIA card.
2. **Download Drivers:** Go to the official [NVIDIA Driver Downloads](https://www.nvidia.com/Download/index.aspx) page.
3. **Select Product:** Choose your GPU (e.g., Product Series: *GeForce GTX 16 Series*, Product: *GeForce GTX 1650*).
4. **Install Type:** Choose **Game Ready Driver** or **Studio Driver**, then download and run the installer. Select the **Express Installation** option.

> [!NOTE]
> Installing the latest NVIDIA driver is crucial. It installs the user-mode CUDA driver (`nvcuda.dll`) required for PyTorch to interface with your GPU.

---

### Step 2: Set Up Your Python Environment
It is best practice to keep your global Python installation clean by creating a virtual environment for each project.

1. **Navigate to your workspace:**
   ```powershell
   cd C:\Python\Openpyxl\GPU
   ```
2. **Create a Virtual Environment:**
   If you want to create a new environment called `env` (similar to your custom `Bala` environment):
   ```powershell
   python -m venv env
   ```
3. **Activate the Environment:**
   ```powershell
   .\env\Scripts\Activate.ps1
   ```

---

### Step 3: Install PyTorch with CUDA Support
Standard `pip install torch` might download a CPU-only version. To get GPU acceleration, you must install the CUDA-enabled build of PyTorch.

1. Go to the [PyTorch Get Started](https://pytorch.org/get-started/locally/) page.
2. Choose your preferences:
   - **Build:** Stable
   - **OS:** Windows
   - **Package:** Pip
   - **Language:** Python
   - **Compute Platform:** CUDA (e.g., CUDA 12.6 or the latest supported version)
3. **Run the Custom Pip Command:**
   Install using the custom index URL. For example, to install PyTorch matching your current CUDA 12.6 environment:
   ```powershell
   pip install torch --index-url https://download.pytorch.org/whl/cu126
   ```

---

### Step 4: Configure Your IDE (VS Code)
To ensure VS Code uses the correct virtual environment instead of a global CPU-only Python:

1. Open your project folder in VS Code.
2. Open the Command Palette by pressing **`Ctrl+Shift+P`**.
3. Type and select **`Python: Select Interpreter`**.
4. Click **`Enter interpreter path...`** and paste:
   ```text
   C:\Python\Bala\Scripts\python.exe
   ```
5. Confirm by opening a terminal in VS Code—it should automatically activate the environment.

---

### Step 5: Test and Verify GPU Acceleration
Create a verification script (like your `gpu_check.py`) and run it:

```python
import torch

print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU Device Name:", torch.cuda.get_device_name(0))
else:
    print("Running on CPU.")
```

Run the script in your terminal:
```powershell
C:\Python\Bala\Scripts\python.exe gpu_check.py
```

---

## ⚡ Basic GPU Computing Example

To utilize your **GeForce GTX 1650**, you need to explicitly move your PyTorch tensors and models to the GPU. Here is a simple demonstration of GPU matrix multiplication:

```python
import torch

# 1. Define target device (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 2. Create tensors directly on the GPU
x = torch.randn(3, 3, device=device)
y = torch.randn(3, 3, device=device)

# 3. Perform a matrix multiplication on the GPU
z = torch.matmul(x, y)

# 4. View results
print("\nTensor x on GPU:\n", x)
print("\nTensor z (Result) on GPU:\n", z)

# 5. Move tensor back to CPU (required for converting to numpy or plotting)
z_cpu = z.to("cpu").numpy()
print("\nResult converted to NumPy on CPU:\n", z_cpu)
```

---

## ❓ Troubleshooting Common CUDA Issues

### 1. `CUDA Available: False`
* **Cause 1:** You installed the CPU-only version of PyTorch.
  * *Fix:* Run `pip list` and check if your PyTorch version has a `+cpu` suffix (e.g. `2.11.0+cpu`). If so, uninstall it (`pip uninstall torch`) and reinstall the CUDA version using the index URL in **Step 3**.
* **Cause 2:** Outdated NVIDIA Drivers.
  * *Fix:* Download and install the latest drivers from NVIDIA's official website.

### 2. Out of Memory (OOM) Errors
* **Cause:** Your GTX 1650 has **4GB of VRAM**. Running huge models (like large LLMs or massive batch sizes in vision models) can exceed this limit.
  * *Fix:* 
    * Reduce the `batch_size` in your training loop.
    * Use mixed-precision training (`torch.cuda.amp.autocast`).
    * Run `torch.cuda.empty_cache()` to free unused memory.
