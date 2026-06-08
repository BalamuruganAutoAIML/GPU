import os
import sys
import time
import subprocess
import threading
import math
import random
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global state for benchmarks and running models
benchmark_thread = None
benchmark_active = False
current_benchmark_model = None
benchmark_metrics = {
    "steps_completed": 0,
    "current_loss": 0.0,
    "efficiency_gflops_per_watt": 0.0,
    "step_latency_ms": 0.0
}

# Try importing torch and pynvml
HAS_TORCH = False
try:
    import torch
    HAS_TORCH = True
except ImportError:
    pass

HAS_NVML = False
try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except Exception:
    pass

def get_gpu_telemetry():
    """Retrieves real GPU telemetry via NVML/PyTorch/nvidia-smi or falls back to realistic simulation."""
    telemetry = {
        "device_name": "NVIDIA CPU-Only Simulation",
        "utilization_gpu": 0,
        "utilization_mem": 0,
        "vram_total_mb": 8192,
        "vram_used_mb": 1200,
        "vram_free_mb": 6992,
        "temperature_c": 42,
        "power_draw_w": 25.0,
        "power_limit_w": 250.0,
        "fan_speed_pct": 20,
        "efficiency_score": "Optimal",
        "has_cuda": False
    }

    if HAS_TORCH and torch.cuda.is_available():
        telemetry["has_cuda"] = True
        telemetry["device_name"] = torch.cuda.get_device_name(0)
        try:
            # PyTorch VRAM metrics
            allocated = torch.cuda.memory_allocated(0) / (1024 * 1024)
            reserved = torch.cuda.memory_reserved(0) / (1024 * 1024)
            telemetry["vram_used_mb"] = int(allocated)
        except Exception:
            pass

    if HAS_NVML:
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Name
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            telemetry["device_name"] = name
            
            # Utilizations
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            telemetry["utilization_gpu"] = util.gpu
            telemetry["utilization_mem"] = util.memory
            
            # VRAM
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            telemetry["vram_total_mb"] = int(mem.total / (1024 * 1024))
            telemetry["vram_used_mb"] = int(mem.used / (1024 * 1024))
            telemetry["vram_free_mb"] = int(mem.free / (1024 * 1024))
            
            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            telemetry["temperature_c"] = temp
            
            # Power
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # milliwatts to watts
            telemetry["power_draw_w"] = round(power, 2)
            
            limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
            telemetry["power_limit_w"] = round(limit, 2)
            
            # Fan Speed
            try:
                fan = pynvml.nvmlDeviceGetFanSpeed(handle)
                telemetry["fan_speed_pct"] = fan
            except Exception:
                # Some laptops/cards don't report fan speed via NVML
                telemetry["fan_speed_pct"] = int(20 + (util.gpu * 0.5))
                
        except Exception as e:
            pass
    else:
        # Fallback to nvidia-smi command line parsing if NVML python bindings are missing
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,temperature.gpu,power.draw,power.limit", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1
            )
            if res.returncode == 0:
                parts = [p.strip() for p in res.stdout.split(',')]
                if len(parts) >= 9:
                    telemetry["device_name"] = parts[0]
                    telemetry["utilization_gpu"] = int(parts[1])
                    telemetry["utilization_mem"] = int(parts[2])
                    telemetry["vram_total_mb"] = int(parts[3])
                    telemetry["vram_used_mb"] = int(parts[4])
                    telemetry["vram_free_mb"] = int(parts[5])
                    telemetry["temperature_c"] = int(parts[6])
                    telemetry["power_draw_w"] = float(parts[7])
                    telemetry["power_limit_w"] = float(parts[8])
                    telemetry["fan_speed_pct"] = int(20 + (telemetry["utilization_gpu"] * 0.5))
        except Exception:
            pass

    # If both NVML and nvidia-smi are missing/fail (e.g. CPU-only machine or driver issues), simulate active realistic loads when benchmark is running
    if telemetry["device_name"] == "NVIDIA CPU-Only Simulation" or not HAS_NVML:
        if benchmark_active:
            # Simulate high-load GPU stats
            telemetry["utilization_gpu"] = random.randint(85, 98)
            telemetry["utilization_mem"] = random.randint(70, 90)
            telemetry["vram_used_mb"] = random.randint(4500, 6800)
            telemetry["vram_free_mb"] = telemetry["vram_total_mb"] - telemetry["vram_used_mb"]
            telemetry["temperature_c"] = random.randint(68, 79)
            telemetry["power_draw_w"] = round(random.uniform(180.0, 235.0), 2)
            telemetry["fan_speed_pct"] = random.randint(55, 75)
        else:
            # Idle/Standard stats
            telemetry["utilization_gpu"] = random.randint(1, 8)
            telemetry["utilization_mem"] = random.randint(2, 12)
            telemetry["vram_used_mb"] = random.randint(800, 1400)
            telemetry["vram_free_mb"] = telemetry["vram_total_mb"] - telemetry["vram_used_mb"]
            telemetry["temperature_c"] = random.randint(38, 44)
            telemetry["power_draw_w"] = round(random.uniform(15.0, 28.0), 2)
            telemetry["fan_speed_pct"] = random.randint(15, 25)

    # Calculate overall GPU efficiency state
    if telemetry["temperature_c"] > 82:
        telemetry["efficiency_score"] = "Thermal Throttling Risk"
    elif telemetry["utilization_gpu"] > 90 and telemetry["power_draw_w"] > (telemetry["power_limit_w"] * 0.9):
        telemetry["efficiency_score"] = "Maximum Power Mode"
    elif telemetry["utilization_gpu"] > 0:
        telemetry["efficiency_score"] = "Highly Efficient"
    else:
        telemetry["efficiency_score"] = "Idle / Energy Saver"

    return telemetry

def run_torch_benchmark():
    """Actual/simulated model workload thread to spike physical/simulated GPU metrics."""
    global benchmark_active, benchmark_metrics
    device = torch.device("cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu")
    
    steps = 0
    loss = 2.5
    
    while benchmark_active:
        start_step = time.time()
        
        if HAS_TORCH and torch.cuda.is_available():
            try:
                # Real GPU work: Heavy Tensor calculations
                size = 2560
                a = torch.randn(size, size, device=device)
                b = torch.randn(size, size, device=device)
                res = torch.matmul(a, b)
                torch.cuda.synchronize()
            except Exception:
                time.sleep(0.05)
        else:
            # Simulation delay
            time.sleep(random.uniform(0.08, 0.15))
            
        steps += 1
        loss = max(0.02, loss * 0.98 - random.uniform(-0.01, 0.02))
        
        # Calculate performance metrics
        latency = (time.time() - start_step) * 1000.0  # in ms
        # GFLOPS = (2 * N^3) / (latency_seconds * 10^9) => ~33.5 GFLOPs for N=2560
        gflops = (2 * (2560 ** 3)) / ((latency / 1000.0) * 1e9) if (HAS_TORCH and torch.cuda.is_available()) else random.uniform(180, 240)
        power = get_gpu_telemetry()["power_draw_w"]
        efficiency = gflops / max(1.0, power)
        
        benchmark_metrics = {
            "steps_completed": steps,
            "current_loss": round(loss, 4),
            "efficiency_gflops_per_watt": round(efficiency, 2),
            "step_latency_ms": round(latency, 2)
        }
        
        time.sleep(0.01)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/gpu_status')
def api_gpu_status():
    status = get_gpu_telemetry()
    status["benchmark_active"] = benchmark_active
    status["current_benchmark_model"] = current_benchmark_model
    status["metrics"] = benchmark_metrics if benchmark_active else None
    return jsonify(status)

@app.route('/api/start_model/<model_name>')
def start_model(model_name):
    global benchmark_thread, benchmark_active, current_benchmark_model, benchmark_metrics
    if not benchmark_active:
        benchmark_active = True
        current_benchmark_model = model_name
        benchmark_metrics = {
            "steps_completed": 0,
            "current_loss": 2.5000,
            "efficiency_gflops_per_watt": 0.0,
            "step_latency_ms": 0.0
        }
        benchmark_thread = threading.Thread(target=run_torch_benchmark, daemon=True)
        benchmark_thread.start()
        return jsonify({"status": "started", "model": model_name})
    return jsonify({"status": "error", "message": "Another model is currently running."})

@app.route('/api/stop_model')
def stop_model():
    global benchmark_active, current_benchmark_model
    if benchmark_active:
        benchmark_active = False
        model = current_benchmark_model
        current_benchmark_model = None
        return jsonify({"status": "stopped", "model": model})
    return jsonify({"status": "idle"})

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    print("Starting Premium GPU Telemetry Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
