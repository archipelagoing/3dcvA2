"""Run the checks and generate the assignment results and reports."""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
for script in ['check.py', 'teddy.py', 'improve_teddy.py', 'fish.py', 'bonus.py',
               'report.py', 'bonus_report.py']:
    print(f'Running {script}', flush=True)
    subprocess.run([sys.executable, '-B', str(root / script)], cwd=root, check=True)
