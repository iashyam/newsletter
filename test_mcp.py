import json
import subprocess
import time

process = subprocess.Popen(
    ["/Users/shyamsunder/github/newsletter/.venv/bin/python", "/Users/shyamsunder/github/newsletter/main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

init_req = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"}
    }
}
process.stdin.write(json.dumps(init_req) + "\n")
process.stdin.flush()

print("INIT REQ:", process.stdout.readline().strip())

# Required post-initialization notification
init_notif = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
process.stdin.write(json.dumps(init_notif) + "\n")
process.stdin.flush()

tools_req = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
}
process.stdin.write(json.dumps(tools_req) + "\n")
process.stdin.flush()

print("TOOLS REQ:", process.stdout.readline().strip())
process.terminate()
