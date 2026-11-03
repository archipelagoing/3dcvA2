"""Collect the reproducible code, required inputs, reports, and key figures."""
import gzip
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

root = Path('submission')
root.mkdir(exist_ok=True)
files = list(Path('src').glob('*.py'))
script_names = ['run_teddy.py', 'run_fish.py', 'run_bonus.py', 'try_teddy_improvements.py',
                'check_stereo.py', 'check_fish_geometry.py', 'check_bonus.py',
                'build_report.py', 'build_bonus_report.py']
files += [Path('scripts') / name for name in script_names]
files += list(Path('teddy').glob('*.pgm'))
files += list(Path('output/pdf').glob('homework2*.pdf'))
files += [Path('output/teddy/metrics.json')]
files += list(Path('output/teddy').glob('census_*.png'))
files += list(Path('output/teddy').glob('disparity_*.png'))
fish = Path('output/fish/scale_0.5_baseline_0.12')
files += [fish / name for name in ['left_rgb.png', 'right_rgb.png', 'left_gray.png', 'right_gray.png', 'metrics.json']]
files += list(fish.glob('disparity_*.png'))
files += [Path('output/bonus') / name for name in ['plane_1_inliers.png', 'plane_2_inliers.png',
          'plane_3_inliers.png', 'image_a.png', 'birdseye_b.png', 'warped_a.png', 'metrics.json']]
files += [Path('output/teddy_improvements') / name for name in
          ['left_right_then_fill_view.png', 'left_right_then_fill_raw.png', 'best_metrics.json']]
for source in sorted(set(files)):
    destination = root / source
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

# Lossless compression keeps the exact original input while reducing folder size.
compressed = root / 'data/data.obj.gz'
compressed.parent.mkdir(exist_ok=True)
with open('data/data.obj', 'rb') as source, gzip.open(compressed, 'wb', compresslevel=9) as target:
    shutil.copyfileobj(source, target, length=1024*1024)

requirements = '''numpy==2.5.4
opencv-python==5.0.0.93
scipy==1.18.1
reportlab==5.1.0
'''
(root / 'requirements.txt').write_text(requirements)
(root / 'run.py').write_text('''"""Unpack the trusted course input and reproduce the assignment outputs."""
import gzip
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
scene = root / 'data/data.obj'
if not scene.exists():
    print('Unpacking the original HW1 input...', flush=True)
    with gzip.open(root / 'data/data.obj.gz', 'rb') as source, scene.open('wb') as target:
        shutil.copyfileobj(source, target, length=1024*1024)
for name in ['check_stereo.py', 'check_fish_geometry.py', 'check_bonus.py',
             'run_teddy.py', 'try_teddy_improvements.py', 'run_fish.py',
             'run_bonus.py', 'build_report.py', 'build_bonus_report.py']:
    print(f'Running {name}', flush=True)
    subprocess.run([sys.executable, str(root / 'scripts' / name)], cwd=root, check=True)
''')
(root / 'READ_ME_FIRST.txt').write_text('''CS 532 - Assignment 2, including the optional bonus

START HERE
  output/pdf/homework2_report.pdf - required work and figures
  output/pdf/homework2_bonus.pdf  - RANSAC, ground plane, bird's-eye comparison

CODE
  src/stereo.py                 - census, Hamming cost, aggregation, winner-take-all
  src/pointcloud_renderer.py    - CPU pinhole projection and intrinsic scaling
  src/planes.py                - RANSAC, plane fitting, homography, bilinear warp
  scripts/run_teddy.py          - required Teddy experiment
  scripts/run_fish.py           - rectified fish views and stereo matching
  scripts/run_bonus.py          - plane and homography bonus
  scripts/try_teddy_improvements.py - best refinement; other attempts commented

IMAGES
  output/teddy/                - census and all four disparity results
  output/fish/scale_0.5_baseline_0.12/ - stereo views and all four disparities
  output/bonus/                - three green-inlier renders, image A, B, and warped A
  output/teddy_improvements/   - selected optional refinement
Raw disparity images store disparity values; disparity_view images are scaled
for display. Black may represent invalid pixels. JSON files contain measurements.

REPRODUCE (from this folder; tested with Python 3.12 on Intel macOS)
  python3.12 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python run.py
The run script losslessly unpacks data/data.obj.gz and runs checks/experiments/reports.
No Open3D installation is required for this CPU pipeline. Dependencies listed
here cover only the included code, rather than the full development environment.
A first dependency installation in a clean environment has not been tested here.

INPUTS
  teddy/ contains the supplied stereo pair and ground truth.
  data/data.obj.gz contains the exact original HW1 scene, compressed losslessly.
The original file is about 267 MiB; unpacking it requires additional disk space.
Only use the trusted course pickle. SHA256SUMS.json checks packaged-file integrity.

BEFORE UPLOADING
Confirm the course's Teddy error-mask convention and quarter-resolution wording.
Current fish run uses quarter total pixels (scale 0.5). Reports state the assumptions.
Add student identification if required. Nothing has been uploaded to Canvas.
''')
manifest = {}
for path in sorted(root.rglob('*')):
    if path.is_file():
        digest = hashlib.sha256()
        with path.open('rb') as file:
            for chunk in iter(lambda: file.read(1024*1024), b''):
                digest.update(chunk)
        manifest[str(path.relative_to(root))] = digest.hexdigest()
(root / 'SHA256SUMS.json').write_text(json.dumps(manifest, indent=2)+'\n')
archive_path = Path('output/submission/compact_submission.zip')
# The input is already gzip-compressed, so store that stream without recompressing.
with zipfile.ZipFile(archive_path, 'w') as archive:
    for path in sorted(root.rglob('*')):
        if path.is_file():
            compression = zipfile.ZIP_STORED if path.suffix=='.gz' else zipfile.ZIP_DEFLATED
            archive.write(path, str(path), compress_type=compression, compresslevel=9)
size = sum(p.stat().st_size for p in root.rglob('*') if p.is_file()) / 1024**2
print(f'Created {root}/: {len(manifest)+1} files, {size:.1f} MiB')
print(f'ZIP: {archive_path}, {archive_path.stat().st_size/1024**2:.1f} MiB')
