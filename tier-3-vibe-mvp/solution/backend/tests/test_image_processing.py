import io

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.errors import APIError
from app.services.image_processing import process_cover_image


def _image_bytes(fmt, size=(800, 600), color="red", exif=None):
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    kwargs = {}
    if exif is not None:
        kwargs["exif"] = exif
    img.save(buf, format=fmt, **kwargs)
    buf.seek(0)
    return buf


@pytest.mark.parametrize("fmt,ext", [("JPEG", "jpg"), ("PNG", "png"), ("WEBP", "webp")])
def test_accepts_each_allowed_format_and_uses_server_generated_filename(app, fmt, ext):
    with app.app_context():
        fs = FileStorage(stream=_image_bytes(fmt), filename=f"my-original-name.{ext}")
        relative_path = process_cover_image(fs)

        assert relative_path.startswith("events/")
        assert relative_path.endswith(f".{ext}")
        assert "my-original-name" not in relative_path  # never the client's filename


def test_no_file_returns_none(app):
    with app.app_context():
        assert process_cover_image(None) is None


def test_too_small_dimensions_rejected(app):
    with app.app_context():
        fs = FileStorage(
            stream=_image_bytes("PNG", size=(100, 100)), filename="small.png"
        )
        with pytest.raises(APIError) as exc_info:
            process_cover_image(fs)
        assert exc_info.value.status_code == 400


def test_too_large_dimensions_rejected(app):
    with app.app_context():
        fs = FileStorage(
            stream=_image_bytes("PNG", size=(4500, 4500)), filename="huge.png"
        )
        with pytest.raises(APIError):
            process_cover_image(fs)


def test_oversized_file_rejected(app):
    with app.app_context():
        # A real image whose byte size still exceeds the 5MB cap the app
        # config sets in tests (padded with an incompressible random tail).
        import os

        buf = _image_bytes("PNG", size=(1000, 1000))
        padded = io.BytesIO(buf.read() + os.urandom(6 * 1024 * 1024))
        fs = FileStorage(stream=padded, filename="big.png")
        with pytest.raises(APIError):
            process_cover_image(fs)


def test_non_image_content_rejected_regardless_of_extension(app):
    with app.app_context():
        fs = FileStorage(
            stream=io.BytesIO(b"this is not an image, just text"), filename="fake.jpg"
        )
        with pytest.raises(APIError):
            process_cover_image(fs)


def test_svg_content_rejected(app):
    """SVG can carry embedded scripts — BRIEF explicitly calls this out."""
    with app.app_context():
        svg = b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>"
        fs = FileStorage(stream=io.BytesIO(svg), filename="fake.png")
        with pytest.raises(APIError):
            process_cover_image(fs)


def test_exif_metadata_is_stripped(app):
    with app.app_context():
        exif = Image.Exif()
        exif[0x0110] = "Suspicious Camera Model"  # Model tag
        fs = FileStorage(
            stream=_image_bytes("JPEG", exif=exif.tobytes()), filename="withexif.jpg"
        )
        relative_path = process_cover_image(fs)

        saved_path = app.config["UPLOAD_FOLDER"] + "/" + relative_path.split("/")[-1]
        reloaded = Image.open(saved_path)
        assert not reloaded.getexif()
