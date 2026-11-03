"""Run the documented workflow in order and retain its output and exit statuses."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

scripts = ['check_inputs.py', 'check_renderer.py', 'check_stereo.py', 'run_teddy.py',
           'try_teddy_improvements.py', 'check_fish_geometry.py', 'run_fish.py', 'build_report.py']
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bonus', action='store_true', help='Also run bonus checks, rendering, and report')
args = parser.parse_args()
if args.bonus:
    scripts += ['check_bonus.py', 'run_bonus.py', 'build_bonus_report.py']
folder = Path('output/verification')
folder.mkdir(parents=True, exist_ok=True)
results = []
for name in scripts:
    command = [sys.executable, str(Path('scripts') / name)]
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, text=True)
    (folder / f'{Path(name).stem}.log').write_text(result.stdout + result.stderr)
    results.append({'script': name, 'exit_code': result.returncode,
                    'seconds': round(time.perf_counter() - start, 3)})
    (folder / ('workflow_with_bonus.json' if args.bonus else 'workflow.json')).write_text(json.dumps(results, indent=2) + '\n')
    print(f'{name}: {"PASS" if result.returncode == 0 else "FAIL"}', flush=True)
    if result.returncode:
        print(result.stdout + result.stderr)
        sys.exit(result.returncode)
print('PASS: complete workflow; logs in output/verification', flush=True)
