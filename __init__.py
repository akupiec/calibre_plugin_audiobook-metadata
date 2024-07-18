from datetime import date
import io

from calibre.customize import MetadataReaderPlugin
from calibre.ebooks.metadata.book.base import Metadata
from PIL import Image
from calibre_plugins.audiobook_metadata.tinytag import TinyTag


class AudioBookPlugin(MetadataReaderPlugin):
    file_types = {"m4b", "m4a"}
    author = "Artur Kupiec"

    name = "Read Audiobooks metadata"
    description = "Read metadata from m4b,m4a files, perhaps more in future..."
    version = (0, 1, 1)
    minimum_calibre_version = (7, 0, 0)
    can_be_disabled = False

    def get_metadata(self, stream, type) -> Metadata:
        tag = TinyTag.get(filename=stream.name, file_obj=stream, image=True)

        title = get_title_form_tag(tag)
        authors = [tag.albumartist, tag.artist, tag.composer]
        meta = Metadata(title, authors)

        if tag.year is not None:
            meta.pubdate = date(int(tag.year), 1, 1)

        image_bytes = tag.get_image()
        if image_bytes is not None:
            image = Image.open(io.BytesIO(image_bytes))
            if image.format is not None:
                format_type = image.format.lower()
                meta.cover_data = (format_type, image_bytes)

        if tag.extra is not None and "copyright" in tag.extra:
            meta.rights = tag.extra["copyright"]

        if tag.genre is not None:
            meta.tags = tuple(tag.genre.split(", "))

        meta.comments = tag.comment
        meta.performer = tag.composer

        return meta


def join_strings_ignore_none(strings, delimiter=' & '):
    return delimiter.join([s for s in strings if s is not None])


def get_title_form_tag(tag):
    title = tag.album or tag.title
    if title is None:
        return None
    return title.strip().rstrip(" (Unabridged)")