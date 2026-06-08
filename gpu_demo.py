import torch
import time

# Check if CUDA (GPU) is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

if not torch.cuda.is_available():
    print("GPU is not available. Please follow the instructions in GPU_Configuration_Guide.md to configure it.")
else:
    print(f"Active GPU: {torch.cuda.get_device_name(0)}")
    
    # Let's run a simple performance test!
    size = 4000
    print(f"\n--- Running Benchmark: Matrix Multiplication of ({size}x{size}) matrices ---")
    
    # CPU calculation
    start_cpu = time.time()
    tensor_cpu_a = torch.randn(size, size)
    tensor_cpu_b = torch.randn(size, size)
    res_cpu = torch.matmul(tensor_cpu_a, tensor_cpu_b)
    time_cpu = time.time() - start_cpu
    print(f"CPU calculation took: {time_cpu:.4f} seconds")
    
    # GPU calculation
    start_gpu = time.time()
    tensor_gpu_a = torch.randn(size, size, device=device)
    tensor_gpu_b = torch.randn(size, size, device=device)
    # Warmup
    res_gpu = torch.matmul(tensor_gpu_a, tensor_gpu_b)
    torch.cuda.synchronize() # Wait for GPU to finish execution
    
    # Actual timed GPU operation
    start_gpu_timed = time.time()
    res_gpu = torch.matmul(tensor_gpu_a, tensor_gpu_b)
    torch.cuda.synchronize()
    time_gpu = time.time() - start_gpu_timed
    print(f"GPU calculation took: {time_gpu:.4f} seconds")
    
    # Calculate speedup
    speedup = time_cpu / time_gpu
    print(f"\n[SPEEDUP] The GPU is {speedup:.1f}x FASTER than the CPU for this matrix multiplication!")
    
    # Move result back to CPU
    res_host = res_gpu.cpu().numpy()
    print("Success: Verified calculation and moved tensor back to CPU RAM.")
