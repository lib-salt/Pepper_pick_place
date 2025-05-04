import subprocess
import os
import sys

# === USER CONFIGURATION SECTION ===
env_1 = r"pepper27" # Python 2.7 environment
env_2 = "pepper3"   # Python 3 environment
# ====================================


base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
base_dir = os.path.abspath(base_dir)

script_1 = os.path.join(base_dir, "pepper_pipeline", "main.py")
script_2 = os.path.join(base_dir, "object_recognition", "stream.py")

# Open Terminal 1 (Python 2.7)
subprocess.Popen([
    "cmd.exe", "/k",
    f'call conda activate {env_1} && python {script_1}'
])

# Open Terminal 2 (Python 3.12)
subprocess.Popen([
    "cmd.exe", "/k",
    f'call conda activate {env_2} && python {script_2}'
])