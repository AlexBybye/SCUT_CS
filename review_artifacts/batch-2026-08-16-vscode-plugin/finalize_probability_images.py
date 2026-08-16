from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
FONT = Path("/System/Library/Fonts/Supplemental/Songti.ttc")
SVG_NS = "{http://www.w3.org/2000/svg}"


def overlay_songti(image: Image.Image, svg_path: Path) -> None:
    tree = ET.parse(svg_path)
    svg = tree.getroot()
    view_box = [float(value) for value in svg.attrib["viewBox"].split()]
    scale_x = image.width / view_box[2]
    scale_y = image.height / view_box[3]
    draw = ImageDraw.Draw(image)

    for position in svg.iter(f"{SVG_NS}tspan"):
        if position.attrib.get("class") != "TextPosition":
            continue
        x = float(position.attrib.get("x", "0")) * scale_x
        y = float(position.attrib.get("y", "0")) * scale_y
        for span in position:
            text = span.text or ""
            if span.attrib.get("font-family") != "宋体" or not text.strip():
                continue
            size_match = re.match(r"([0-9.]+)", span.attrib.get("font-size", "423"))
            size = max(8, round(float(size_match.group(1)) * scale_y))
            font = ImageFont.truetype(str(FONT), size=size, index=0)
            bbox = draw.textbbox((x, y), text, font=font, anchor="ls")
            cover = (bbox[0] - 2, bbox[1] - 2, bbox[2] + 2, bbox[3] + 2)
            draw.rectangle(cover, fill="white")
            draw.text((x, y), text, font=font, fill="black", anchor="ls")


def crop_and_save(png_path: Path, svg_path: Path, output_path: Path) -> None:
    image = Image.open(png_path).convert("RGB")
    if svg_path.exists():
        overlay_songti(image, svg_path)
    white = Image.new("RGB", image.size, "white")
    bbox = ImageChops.difference(image, white).getbbox()
    if bbox is None:
        cropped = Image.new("RGB", (1, 1), "white")
    else:
        left, top, right, bottom = bbox
        padding = 2
        cropped = image.crop(
            (
                max(0, left - padding),
                max(0, top - padding),
                min(image.width, right + padding),
                min(image.height, bottom + padding),
            )
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_path, format="PNG", optimize=True)


def finalize(source_id: str, png_dir: Path, svg_dir: Path) -> None:
    output_dir = ROOT / "knowledge/probability/assets" / source_id
    for png_path in sorted(png_dir.glob("image_*.png")):
        number = png_path.stem.split("_")[-1]
        output_path = output_dir / f"image-{number}.png"
        crop_and_save(png_path, svg_dir / f"image_{number}.svg", output_path)


def make_contact_sheet() -> None:
    samples = [
        ("004/013 start", ROOT / "knowledge/probability/assets/probability-theory-004/image-013.png"),
        ("004/056 middle", ROOT / "knowledge/probability/assets/probability-theory-004/image-056.png"),
        ("004/112 end", ROOT / "knowledge/probability/assets/probability-theory-004/image-112.png"),
        ("006/001 start", ROOT / "knowledge/probability/assets/probability-theory-006/image-001.png"),
        ("006/149 table", ROOT / "knowledge/probability/assets/probability-theory-006/image-149.png"),
        ("006/255 end", ROOT / "knowledge/probability/assets/probability-theory-006/image-255.png"),
    ]
    for source_id, numbers in (
        ("probability-theory-004", (26, 34, 88, 90, 103, 106, 108)),
        ("probability-theory-006", (52, 163, 183, 215, 216, 228, 234)),
    ):
        short = source_id[-3:]
        for number in numbers:
            samples.append(
                (
                    f"{short}/{number:03d} CJK",
                    ROOT / f"knowledge/probability/assets/{source_id}/image-{number:03d}.png",
                )
            )

    columns, cell_width, cell_height = 4, 360, 220
    rows = (len(samples) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), "white")
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype(str(FONT), size=18, index=0)
    for index, (label, path) in enumerate(samples):
        image = Image.open(path).convert("RGB")
        thumb = ImageOps.contain(image, (cell_width - 20, cell_height - 42))
        x = (index % columns) * cell_width
        y = (index // columns) * cell_height
        sheet.paste(thumb, (x + (cell_width - thumb.width) // 2, y + 30))
        draw.text((x + 8, y + 6), label, font=label_font, fill="black")
        draw.rectangle((x, y, x + cell_width - 1, y + cell_height - 1), outline="#cccccc")
    sheet.save("/private/tmp/probability-answer-contact-sheet.png", optimize=True)


def crop_source_diagram() -> None:
    page = Image.open("/private/tmp/probability-004-page-4.png").convert("RGB")
    diagram = page.crop((170, 310, 455, 595))
    white = Image.new("RGB", diagram.size, "white")
    bbox = ImageChops.difference(diagram, white).getbbox()
    if bbox is None:
        raise RuntimeError("source diagram crop is empty")
    left, top, right, bottom = bbox
    padding = 8
    diagram = diagram.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(diagram.width, right + padding),
            min(diagram.height, bottom + padding),
        )
    )
    diagram.save(
        ROOT / "knowledge/probability/assets/probability-theory-004/diagram-001.png",
        optimize=True,
    )


if __name__ == "__main__":
    finalize(
        "probability-theory-004",
        Path("/private/tmp/prob-png-004"),
        Path("/private/tmp/prob-svg-004"),
    )
    finalize(
        "probability-theory-006",
        Path("/private/tmp/prob-png-006"),
        Path("/private/tmp/prob-svg-006"),
    )
    crop_source_diagram()
    make_contact_sheet()
