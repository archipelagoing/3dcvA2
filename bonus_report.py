"""Build a separate bonus report so the required report stays unchanged."""
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from report import paragraph, table, image_grid, PAGE_WIDTH, PAGE_HEIGHT, MARGIN

FOLDER = Path('results')
OUTPUT = Path('results/bonus.pdf')


def heading(pdf, title, page):
    pdf.setFillColor(colors.HexColor('#153b50'))
    pdf.setFont('Helvetica-Bold',20)
    pdf.drawString(MARGIN,743,title)
    pdf.setStrokeColor(colors.HexColor('#a5bdc9'))
    pdf.line(MARGIN,728,PAGE_WIDTH-MARGIN,728)
    pdf.setFont('Helvetica',8)
    pdf.drawString(MARGIN,27,'CS 532 | Homework 2 bonus | Planes and homography')
    pdf.drawRightString(PAGE_WIDTH-MARGIN,27,str(page))


def main():
    data=json.loads((FOLDER/'bonus_metrics.json').read_text())
    pdf=canvas.Canvas(str(OUTPUT),pagesize=(PAGE_WIDTH,PAGE_HEIGHT))
    pdf.setTitle('CS 532 Homework 2 Bonus - Planes and Homography')
    heading(pdf,'Planes and a bird\'s-eye view',1)
    top=paragraph(pdf,'<b>RANSAC.</b> Use a unit-normal plane n.X+d=0. Sample three points, '
        'form their 3 x 4 homogeneous matrix, and find the plane as its SVD null space. '
        'Reject collinear triples. A point is an inlier if |n.X+d| &lt; 0.025 scene units. '
        'Score hypotheses on a fixed random sample of 30,000 remaining points (seed 532). '
        'Use an adaptive trial budget targeting 0.999 sampling confidence, with a minimum '
        'of 100 and maximum of 2,000 trials. The cap means the confidence target is not '
        'guaranteed for small planes. Refine using covariance least squares, classify the '
        'full remaining cloud, refine again, and remove that consensus before repeating.',710)
    rows=[['Plane','Full-cloud inliers','Trials','Interpretation']]
    for result in data['planes']:
        number=result['number']
        rows.append([str(number),f"{result['inliers']:,}",str(result['ransac_trials']),
                     'Ground' if result['ground_candidate'] else ('Background wall' if number==1 else 'Fountain facade')])
    top=table(pdf,rows,top,[55,150,65,258])
    plane=data['ground_plane']
    top=paragraph(pdf,f'<b>Ground plane.</b> Plane {data["ground_plane_number"]}: '
        f'n=({plane[0]:.8f}, {plane[1]:.8f}, {plane[2]:.8f}), d={plane[3]:.8f}. '
        'Coordinates are in the original camera/world frame, with image y increasing downward. '
        'An upright-ground prior (|ny| &gt; 0.85 and positive median y) identifies a candidate; '
        'visual inspection confirms the green points cover the floor. Previous planes are '
        'absent from later renders. Recolor only current inliers green; do not fill holes.',top)
    top=paragraph(pdf,'<b>Camera poses.</b> Image A uses Ra=I, ta=0. Render 768 x 512 with '
        'fx=689.875, fy=691.05, cx=380.175, cy=251.70. Project the median ground location '
        'onto the plane for the target. Put camera B along the normal above that target '
        f'at height {data["height_above_ground"]:.4f} scene units. Point its optical axis '
        'along -n, with x aligned to the projected world-x direction. Choose height from '
        'the 98th-percentile ground footprint to leave a framing margin. Use tb=-Rb Cb. '
        'The exact K, poses, target, and homography are saved in results/bonus_metrics.json.',top)
    top=paragraph(pdf,'<b>Plane-induced homography.</b> Since the first camera is the world '
        'frame, H=Kb (Rb - tb n^T/d) Ka^-1 maps A pixels to B pixels. This follows by '
        'substituting n.X=-d for points on the ground. Inverse-map destination pixels '
        'through H^-1 and implement four-neighbor bilinear interpolation directly. '
        'Pixels outside A stay black. No library homography estimation or image warp is used.',top)
    top=paragraph(pdf,'<b>Comparison.</b> The ground footprint agrees between directly rendered '
        'B and warped A, but the fountain is stretched into the floor by the homography. '
        'The 3D renderer retains object height, occlusions, and missing surfaces. The '
        'source point cloud was captured from one view, so the overhead render has '
        'large holes and sparse surfaces; the warp interpolates existing source pixels. '
        'A single plane homography cannot correctly move objects off that plane.',top)
    top=paragraph(pdf,f'<b>Verification.</b> Tests passed for exact/noisy planes, outliers, '
        'degenerate triples, pose orthonormality, sign-invariant homography, and identity, '
        'translated, and half-pixel interpolation examples. Projected points placed exactly '
        f'on the fitted plane agree under H and direct projection to within '
        f'{data["max_plane_projection_error_pixels"]:.2g} pixels. This is a geometric test, '
        'not a claim that the full images match. Run check.py, '
        'bonus.py, and bonus_report.py.',top)
    if top<45:raise RuntimeError('Bonus explanation exceeds one page')
    pdf.showPage()
    heading(pdf,'Sequential plane detection',2)
    image_grid(pdf,[(FOLDER/'bonus_plane_1_inliers.png','1 | Background wall'),
                    (FOLDER/'bonus_plane_2_inliers.png','2 | Ground plane'),
                    (FOLDER/'bonus_plane_3_inliers.png','3 | Fountain facade'),
                    (FOLDER/'bonus_image_a.png','Original scene | Image A')])
    pdf.showPage()
    heading(pdf,'Direct rendering versus warping',3)
    image_grid(pdf,[(FOLDER/'bonus_birdseye_b.png','Image B | Rendered from above'),
                    (FOLDER/'bonus_warped_a.png','Image A | Ground-plane warp'),
                    (FOLDER/'bonus_image_a.png','Image A | Original viewpoint'),
                    (FOLDER/'bonus_warp_valid.png','Warp coverage | White = inside A')])
    pdf.save()
    print(f'Saved {OUTPUT}')


if __name__=='__main__':main()
