"""Package source, course inputs, generated results, and the report for submission."""
import hashlib
import json
import zipfile
from pathlib import Path

has_bonus = Path('output/bonus/metrics.json').exists()
archive_name = 'homework2_submission_with_bonus.zip' if has_bonus else 'homework2_submission.zip'
archive_path = Path('output/submission') / archive_name
archive_path.parent.mkdir(parents=True, exist_ok=True)
files = [Path('requirements.txt'), Path('LICENSE')]
for folder, pattern in [('src', '*.py'), ('scripts', '*.py'), ('teddy', '*.pgm'),
                        ('output/teddy', '*'), ('output/teddy_improvements', '*'),
                        ('output/fish/scale_0.5_baseline_0.12', '*'),
                        ('output/verification', '*')]:
    files.extend(path for path in Path(folder).glob(pattern) if path.is_file())
files += [Path('data/data.obj'), Path('output/pdf/homework2_report.pdf')]
if has_bonus:
    files.extend(path for path in Path('output/bonus').glob('*') if path.is_file())
    files.append(Path('output/pdf/homework2_bonus.pdf'))
# The input checker compares extracted Teddy files against their source archive.
files.append(Path('teddy 2.zip'))
instructions = '''CS 532 - Homework 2

CONTENTS
src/ and scripts/: source code and repeatable checks (no installed libraries).
teddy/: supplied stereo images and ground truth; original archive also included.
data/data.obj: trusted HW1 fish point cloud.
output/teddy/: required unfiltered Teddy results.
output/teddy_improvements/: optional refinement results, kept separate.
output/fish/scale_0.5_baseline_0.12/: fish views, maps, masks, and geometry.
output/pdf/homework2_report.pdf: report (one explanatory page, four figure pages).
output/verification/: recorded workflow exit statuses and logs.
MANIFEST.json: SHA-256 checksums for packaged files.

RUN FROM THIS DIRECTORY
Tested locally with Python 3.12 on Intel macOS.
  python3.12 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python scripts/verify_workflow.py

The workflow checks inputs and rendering, evaluates Teddy, runs the selected
optional refinement, checks fish geometry, evaluates fish, and rebuilds the PDF.
The original Open3D diagnostic is included for reference but is not run because
its headless backend is unsupported on the tested Mac. CPU rendering is used.
The trusted course data.obj is a pickle; do not replace it with an untrusted file.

ASSUMPTIONS TO CONFIRM BEFORE SUBMISSION
Quarter resolution is interpreted as quarter total pixels (scale 0.5).
Use scripts/run_fish.py --scale 0.25 if quarter width/height is required; this
writes a different output folder and requires adapting the report's fish path.
Teddy report states both full-image and shared-interior error conventions.
Ground-truth zeros are excluded only in explicitly masked metrics.
Physical length units are unconfirmed; use consistent scene units.
The report has no student identification filled in; add it if required.
No optional bonus or video is included; the required stereo outputs are images.
Course confirmation and Canvas submission are to be handled by the student.
'''
if has_bonus:
    instructions = instructions.replace('No optional bonus or video is included; the required stereo outputs are images.',
        'The optional plane/homography bonus IS included under output/bonus/ and in\noutput/pdf/homework2_bonus.pdf. No video is required for these stereo results.')
    instructions += '\nBONUS COMMANDS\n  .venv/bin/python scripts/check_bonus.py\n  .venv/bin/python scripts/run_bonus.py\n  .venv/bin/python scripts/build_bonus_report.py\n  .venv/bin/python scripts/verify_workflow.py --bonus\n'

manifest = {}
with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in sorted(set(files)):
        digest = hashlib.sha256()
        with path.open('rb') as source, archive.open('homework2/' + str(path), 'w', force_zip64=True) as target:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
                target.write(chunk)
        manifest[str(path)] = digest.hexdigest()
    archive.writestr('homework2/RUNNING.txt', instructions)
    manifest['RUNNING.txt'] = hashlib.sha256(instructions.encode()).hexdigest()
    archive.writestr('homework2/MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
print(f'Created {archive_path}: {archive_path.stat().st_size / 1024**2:.1f} MiB, {len(manifest)} files')
