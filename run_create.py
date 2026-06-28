import subprocess
import sys
import os

# Get the current python path dynamically
venv_python = sys.executable
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_superuser.py")

result = subprocess.run([venv_python, script_path], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)