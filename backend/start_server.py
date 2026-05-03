import subprocess, sys, os

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

p = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=r"D:\ai-carbon-system\backend",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

print(f"Backend PID: {p.pid}")
for line in p.stdout:
    print(line.decode("utf-8", errors="replace"), end="")