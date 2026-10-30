"""Generate Turno's simple clock icon from native drawing primitives."""
from pathlib import Path
from PIL import Image, ImageDraw


def make_icon(destination: Path):
    size = 256
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 248, 248), radius=52, fill="#426483")
    draw.ellipse((48, 48, 208, 208), fill="white")
    draw.line((128, 81, 128, 128, 162, 150), fill="#426483", width=13)
    draw.ellipse((121, 121, 135, 135), fill="#426483")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    make_icon(Path(__file__).resolve().parents[1] / "build" / "turno.ico")
