from PIL import Image

THUMB_SIZE = (256, 256)


def make_thumbnail(src, dst):
    with Image.open(src) as img:
        img.thumbnail(THUMB_SIZE)
        img.save(dst, "JPEG", quality=85)
