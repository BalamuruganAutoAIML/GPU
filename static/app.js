// State variables
let telemetryChart;
const chartDataLimit = 20; // limit chart to last 20 seconds of data
let timeLabels = [];
let loadData = [];
let tempData = [];
let powerData = [];

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
    initChart();
    // Start periodic polling
    pollTelemetry();
    setInterval(pollTelemetry, 1000);
});

// Initialize Chart.js
function initChart() {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    
    // Create neon gradient fills
    const utilGradient = ctx.createLinearGradient(0, 0, 0, 200);
    utilGradient.addColorStop(0, 'rgba(0, 242, 254, 0.25)');
    utilGradient.addColorStop(1, 'rgba(0, 242, 254, 0.0)');

    const tempGradient = ctx.createLinearGradient(0, 0, 0, 200);
    tempGradient.addColorStop(0, 'rgba(255, 0, 127, 0.2)');
    tempGradient.addColorStop(1, 'rgba(255, 0, 127, 0.0)');

    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [
                {
                    label: 'GPU Load (%)',
                    data: loadData,
                    borderColor: '#00f2fe',
                    borderWidth: 2,
                    backgroundColor: utilGradient,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                },
                {
                    label: 'Temp (°C)',
                    data: tempData,
                    borderColor: '#ff007f',
                    borderWidth: 2,
                    backgroundColor: tempGradient,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                },
                {
                    label: 'Power (W)',
                    data: powerData,
                    borderColor: '#39ff14',
                    borderWidth: 1.5,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Using custom legends in HTML
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)'
                    },
                    ticks: {
                        color: '#8c9ba5',
                        font: { family: 'Rajdhani' }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)'
                    },
                    ticks: {
                        color: '#8c9ba5',
                        font: { family: 'Rajdhani' }
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Poll backend telemetry API
function pollTelemetry() {
    fetch('/api/gpu_status')
        .then(response => response.json())
        .then(data => {
            updateUI(data);
            updateChart(data);
        })
        .catch(err => console.error("Error polling telemetry:", err));
}

// Update text states and progress meters
function updateUI(data) {
    // Hardware Name
    document.getElementById('gpu-device-name').innerText = data.device_name;
    
    // Core parameters
    document.getElementById('val-gpu-util').innerText = data.utilization_gpu;
    document.getElementById('fill-gpu-util').style.width = data.utilization_gpu + '%';
    
    document.getElementById('val-vram-used').innerText = data.vram_used_mb;
    document.getElementById('val-vram-total').innerText = data.vram_total_mb;
    const vramPct = (data.vram_used_mb / data.vram_total_mb) * 100;
    document.getElementById('fill-vram').style.width = vramPct + '%';
    
    document.getElementById('val-temp').innerText = data.temperature_c;
    document.getElementById('fill-temp').style.width = data.temperature_c + '%';
    
    document.getElementById('val-power').innerText = data.power_draw_w.toFixed(1);
    const powerPct = (data.power_draw_w / data.power_limit_w) * 100;
    document.getElementById('fill-power').style.width = Math.min(100, powerPct) + '%';
    
    // Fan speed & thermal state
    document.getElementById('val-fan').innerText = data.fan_speed_pct + '%';
    const stateEl = document.getElementById('state-efficiency');
    stateEl.innerText = data.efficiency_score;
    if (data.efficiency_score.includes("Throttling")) {
        stateEl.className = 'status-warning';
    } else {
        stateEl.className = 'status-ok';
    }

    // Benchmark updates
    const badge = document.getElementById('model-status-badge');
    const abortBtn = document.getElementById('btn-kill-model');
    const activeModelName = document.getElementById('active-model-name');
    
    if (data.benchmark_active) {
        badge.innerText = "EXECUTING";
        badge.className = "status-indicator active";
        abortBtn.disabled = false;
        activeModelName.innerText = data.current_benchmark_model;
        
        // Update benchmark metrics
        document.getElementById('model-steps').innerText = data.metrics.steps_completed;
        document.getElementById('model-latency').innerText = data.metrics.step_latency_ms.toFixed(1);
        document.getElementById('model-efficiency').innerText = data.metrics.efficiency_gflops_per_watt.toFixed(1);
        document.getElementById('model-loss').innerText = data.metrics.current_loss.toFixed(4);
        
        // Log periodically
        if (data.metrics.steps_completed > 0 && data.metrics.steps_completed % 4 === 0) {
            appendLog(`[TRAIN] Step ${data.metrics.steps_completed} completed | Loss: ${data.metrics.current_loss.toFixed(4)} | Latency: ${data.metrics.step_latency_ms.toFixed(1)}ms | Compute Efficiency: ${data.metrics.efficiency_gflops_per_watt.toFixed(1)} GFLOPS/W`, 'metric');
        }
    } else {
        badge.innerText = "STANDBY";
        badge.className = "status-indicator";
        abortBtn.disabled = true;
        activeModelName.innerText = "None Running";
        
        document.getElementById('model-steps').innerText = "0";
        document.getElementById('model-latency').innerText = "0.0";
        document.getElementById('model-efficiency').innerText = "0.0";
        document.getElementById('model-loss').innerText = "0.0000";
    }
}

// Update dynamic line chart
function updateChart(data) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    timeLabels.push(timeStr);
    loadData.push(data.utilization_gpu);
    tempData.push(data.temperature_c);
    powerData.push(data.power_draw_w);
    
    if (timeLabels.length > chartDataLimit) {
        timeLabels.shift();
        loadData.shift();
        tempData.shift();
        powerData.shift();
    }
    
    telemetryChart.update();
}

// Trigger neural network model benchmark
function triggerModel(modelName) {
    appendLog(`[SYSTEM] Initializing weight matrix for ${modelName}...`, 'system');
    fetch(`/api/start_model/${encodeURIComponent(modelName)}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === "started") {
                appendLog(`[SYSTEM] Deployed model: ${modelName} on GPU. Starting computation sweeps...`, 'system');
            } else {
                appendLog(`[ERROR] Deployment failed: ${data.message}`, 'alert');
            }
        });
}

// Abort active execution
function stopModelExecution() {
    appendLog(`[SYSTEM] Interrupt signal sent. Gracefully halting operations...`, 'alert');
    fetch('/api/stop_model')
        .then(res => res.json())
        .then(data => {
            if (data.status === "stopped") {
                appendLog(`[SYSTEM] Execution aborted. Model ${data.model} successfully unloaded from VRAM.`, 'system');
            }
        });
}

// Log utility
function appendLog(message, type = 'info') {
    const logEl = document.getElementById('execution-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerText = message;
    logEl.appendChild(entry);
    logEl.scrollTop = logEl.scrollHeight;
    
    // Maintain maximum log lines
    while (logEl.children.length > 50) {
        logEl.removeChild(logEl.firstChild);
    }
}
