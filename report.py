"""Build the homework report from the saved measurements and output images."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

OUTPUT = Path('results/report.pdf')
TEDDY = Path('results')
FISH = Path('results')
PAGE_WIDTH, PAGE_HEIGHT = 612, 792
MARGIN = 42
TEXT_WIDTH = PAGE_WIDTH - 2 * MARGIN
BODY = ParagraphStyle('body', fontName='Helvetica', fontSize=9, leading=12,
                      textColor=colors.HexColor('#243245'))


def paragraph(pdf, text, top):
    block = Paragraph(text, BODY)
    _, height = block.wrap(TEXT_WIDTH, PAGE_HEIGHT)
    block.drawOn(pdf, MARGIN, top - height)
    return top - height - 9


def heading(pdf, title, page):
    pdf.setFillColor(colors.HexColor('#153b50'))
    pdf.setFont('Helvetica-Bold', 20)
    pdf.drawString(MARGIN, 743, title)
    pdf.setStrokeColor(colors.HexColor('#a5bdc9'))
    pdf.line(MARGIN, 728, PAGE_WIDTH - MARGIN, 728)
    pdf.setFont('Helvetica', 8)
    pdf.setFillColor(colors.HexColor('#5e6c76'))
    pdf.drawString(MARGIN, 27, 'CS 532 | Homework 2 | Required results and stated assumptions')
    pdf.drawRightString(PAGE_WIDTH - MARGIN, 27, str(page))


def table(pdf, rows, top, widths):
    grid = Table(rows, colWidths=widths, rowHeights=22)
    grid.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#153b50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#eff4f6'), colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    _, height = grid.wrap(TEXT_WIDTH, PAGE_HEIGHT)
    grid.drawOn(pdf, MARGIN, top - height)
    return top - height - 12


def image_grid(pdf, panels):
    """Place four labeled images on a page, preserving their aspect ratios."""
    gap = 18
    cell_width = (TEXT_WIDTH - gap) / 2
    for index, (path, label) in enumerate(panels):
        column, row = index % 2, index // 2
        x = MARGIN + column * (cell_width + gap)
        top = 681 - row * 306
        pdf.setFont('Helvetica-Bold', 10)
        pdf.setFillColor(colors.HexColor('#243245'))
        pdf.drawString(x, top, label)
        image = ImageReader(str(path))
        width, height = image.getSize()
        ratio = min(cell_width / width, 267 / height)
        draw_width, draw_height = width * ratio, height * ratio
        pdf.drawImage(image, x + (cell_width - draw_width) / 2, top - 12 - draw_height,
                      width=draw_width, height=draw_height)


def main():
    teddy = json.loads((TEDDY / 'teddy_metrics.json').read_text())['results']
    fish = json.loads((FISH / 'fish_metrics.json').read_text())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    pdf.setTitle('CS 532 Homework 2 - Census Stereo')
    pdf.setAuthor('')
    heading(pdf, 'Census stereo: method and results', 1)
    top = paragraph(pdf, '<b>Problem 1.</b> Compare every neighbor with its center using &lt;, omit the center, '
                    'and encode comparisons in a 64-bit census descriptor. For each left pixel, test right '
                    'pixel x-d, sum descriptor Hamming distances over WA x WA, then select the lowest cost '
                    '(ties choose smaller d). Search d=0..63. Reject candidates whose census or aggregation '
                    'windows cross either image boundary. Pixels without candidates are black.', 710)
    top = paragraph(pdf, '<b>Census display.</b> Show descriptor distance from the all-zero descriptor '
                    '(set-bit count), mapping the complete possible range 0..8 or 0..48 to 0..255. Both '
                    'sizes show similar relative-brightness structure, but 7 x 7 uses more context and '
                    'has finer count levels. These displays discard bit arrangement; matching uses every bit.', top)
    top = paragraph(pdf, '<b>Evaluation.</b> Ground truth is floor(stored/4 + 0.5). Absolute error &gt;1 is bad. '
                    'Whole image counts all 168,750 pixels, including invalid black borders and GT zeros. '
                    'Shared interior uses the same 131,311 pixels: rows [7,368), columns [70,443), GT&gt;0. '
                    'GT-zero exclusion and border treatment are explicit assumptions requiring course confirmation.', top)
    rows = [['Wc', 'WA', 'Whole image error', 'Shared interior error']]
    for result in teddy:
        rows.append([str(result['census_size']), str(result['aggregation_size']),
                     f"{result['full_image_including_invalid']['error_percent']:.4f}%",
                     f"{result['common_interior']['error_percent']:.4f}%"])
    top = table(pdf, rows, top, [45, 45, 219, 219])
    top = paragraph(pdf, '<b>Problem 2.</b> Interpret quarter resolution as quarter total pixels: '
                    '3072 x 2048 becomes 1536 x 1024. Scale both first rows of K by 0.5: '
                    'fx=1379.75, fy=1382.10, cx=760.35, cy=503.40. Image dimensions/focal lengths and '
                    'normalized principal point remain constant, preserving both fields of view. This '
                    'resolution interpretation still needs confirmation; scale 0.25 is configurable.', top)
    top = paragraph(pdf, '<b>Geometry.</b> Use R=I, left center (0,0,0), right center (0.12,0,0). '
                    'World-to-camera t values are (0,0,0) and (-0.12,0,0). Shared fixed K and parallel axes '
                    'give equal vertical coordinates. The baseline targets about 43 pixels at the closest '
                    'surface: d=fx B/Z. Scene Z=3.8663..9.6567 predicts d=17.1456..42.8241. Search 0..44 '
                    'covers depths from 3.7630 toward infinity (d=0 is the infinite-depth limit). All lengths '
                    'are scene units; physical scale is unconfirmed.', top)
    top = paragraph(pdf, '<b>Rendering and findings.</b> NumPy pinhole projection with a nearest-depth buffer '
                    'replaces unsupported Open3D headless rendering on this Mac. No maximum filter or hole '
                    'filling is used. Grayscale is round(0.30R + 0.59G + 0.11B). Run the same unfiltered '
                    'matcher for all four settings. Against a depth-derived reference on 1,379,716 '
                    'mutually visible interior pixels, errors are 0.7700%, 0.2253%, 0.3017%, 0.2886% '
                    'in (3,5), (3,9), (7,5), (7,9) order. This synthetic diagnostic excludes holes and is '
                    'not independent ground truth. Larger windows reduce speckle but blur boundaries. '
                    'New viewpoints expose missing surfaces; occlusions remain difficult.', top)
    top = paragraph(pdf, '<b>Verification.</b> Hand-computed census, direct Hamming/window sums, shifted and '
                    'identical inputs, brute-force WTA, rectification, RGB readback, and calibration checks '
                    'passed. Reproduce with teddy.py and fish.py using the documented '
                    'Python environment. Figures follow; optional refinements are separate from these required results.', top)
    if top < 48:
        raise RuntimeError(f'Explanatory text overflows its one-page limit: {top}')
    pdf.showPage()
    heading(pdf, 'Teddy: census visualizations', 2)
    paragraph(pdf, 'Black to white: set-bit count 0..8 (Wc=3) or 0..48 (Wc=7).', 711)
    image_grid(pdf, [(TEDDY / f'teddy_census_{side}_wc{size}.png', f'{side.title()} | Wc = {size}')
                     for size in (3, 7) for side in ('left', 'right')])
    pdf.showPage()
    heading(pdf, 'Teddy: disparity maps', 3)
    paragraph(pdf, 'Black to white: disparity 0..63 pixels. Invalid borders are also black.', 711)
    image_grid(pdf, [(TEDDY / f'teddy_disparity_view_wc{r["census_size"]}_wa{r["aggregation_size"]}.png',
                     f'Wc = {r["census_size"]}, WA = {r["aggregation_size"]}') for r in teddy])
    pdf.showPage()
    heading(pdf, 'Fish: rectified stereo images', 4)
    paragraph(pdf, '1536 x 1024 pixels per view | Baseline 0.12 scene units | No hole filling.', 711)
    image_grid(pdf, [(FISH / f'fish_{side}_{kind}.png', f'{side.title()} | {kind.upper()}')
                     for kind in ('rgb', 'gray') for side in ('left', 'right')])
    pdf.showPage()
    heading(pdf, 'Fish: disparity maps', 5)
    paragraph(pdf, 'Black to white: disparity 0..44 pixels. Invalid borders and unsupported regions remain.', 711)
    image_grid(pdf, [(FISH / f'fish_disparity_view_wc{r["census_size"]}_wa{r["aggregation_size"]}.png',
                     f'Wc = {r["census_size"]}, WA = {r["aggregation_size"]}') for r in fish['results']])
    pdf.save()
    print(f'Saved {OUTPUT}; explanatory content ends at y={top:.1f}')


if __name__ == '__main__':
    main()
