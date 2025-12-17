import psutil
import time
from datetime import datetime

LOG_FILE = "upload_log.txt"
INTERVAL = 3
UPLOAD_THRESHOLD = 1024 * 500  # 500 KB

prev_net = psutil.net_io_counters()
prev_sent = prev_net.bytes_sent

print("[+] Kali Linux Upload Monitor Started")
print("[+] Press CTRL+C to stop\n")

while True:
    time.sleep(INTERVAL)

    net = psutil.net_io_counters()
    delta_sent = net.bytes_sent - prev_sent
    prev_sent = net.bytes_sent

    if delta_sent < UPLOAD_THRESHOLD:
        continue

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Find active TCP connections
    for conn in psutil.net_connections(kind="inet"):
        if conn.status != psutil.CONN_ESTABLISHED:
            continue
        if not conn.raddr or not conn.pid:
            continue

        try:
            proc = psutil.Process(conn.pid)
            pname = proc.name()
        except:
            continue

        msg = (
            f"{now}  PID:{conn.pid}  Process:{pname}  "
            f"Local:{conn.laddr.ip}:{conn.laddr.port}  "
            f"Remote:{conn.raddr.ip}:{conn.raddr.port}  "
            f"Uploaded:{delta_sent/1024:.2f} KB"
        )

        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")

        break   # log once per interval
