import socket
from flask import Flask
from project_copy import SystemMonitor
monitor = SystemMonitor()

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200
@app.route("/")
def home():
    monitor.write_to_database()
    totalmem, leftmem, percentmem, usedmem = monitor.get_memtotal()
    totalswap, usedswap, freeswap, percentswap = monitor.get_swap()
    bsent, brecieve, psent, preceive, errin, errout, dropin, dropout = monitor.get_traffic()
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="10">
        <title>Raspberry Pi Monitor</title>
    </head>
    <body>
    <h1>Raspberry Pi Monitor</h1>

    Container: {socket.gethostname()}<br>
    Username: {monitor.get_username()}<br>
    IP: {monitor.get_ip()}<br>
    Pi: {monitor.get_pyinfo()}<br>
    Uptime: {monitor.get_uptime()}<br>
    Python Version: {monitor.get_python_version()}<br>
    Storage Usage: {monitor.get_usage()}Gb/{monitor.get_total()}Gb ({monitor.get_disk_usage()}%)<br>
    Memory Usage: {usedmem}MB/{totalmem}MB ({percentmem}%)<br>
    Swap Usage: {usedswap}MB/{totalswap}MB ({percentswap}%)<br>
    CPU Usage: {monitor.get_cpuusage()}%<br>
    CPU Temperature: {monitor.get_cputemp()}C<br>
    Voltage: {monitor.get_voltage()}<br>
    Throttle Status {monitor.get_throttle()}<br>
    Network Traffic: Sent: {bsent}MB, Received: {brecieve}MB, Packets Sent: {psent}, Packets Received: {preceive}, <br>
    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)