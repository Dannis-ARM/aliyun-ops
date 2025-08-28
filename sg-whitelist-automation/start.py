import os
from pathlib import Path
import subprocess

project_dir = Path(__file__).parent

os.chdir(project_dir)

# Run build.ps1
build_script = project_dir / 'build.ps1'
subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(build_script)], check=True)

print("\n")
# Run the built executable
exe_path = project_dir / 'dist' / 'sg-whitelist-automation.exe'
subprocess.run([str(exe_path)], check=True)