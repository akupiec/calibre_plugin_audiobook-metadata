from tinytag import TinyTag
from PIL import Image
import io




def join_strings_ignore_none(strings, delimiter=' & '):
    return delimiter.join([s for s in strings if s is not None])


file_obj = io.open('test.m4b', 'rb')
print('name %s' % file_obj.name)
print('file_obj %s' % file_obj)
tag = TinyTag.get(filename=file_obj.name, file_obj=file_obj, image=True)

authors = join_strings_ignore_none([tag.albumartist, tag.artist, tag.composer])

image_data = tag.get_image()
print('This track is by %s.' % authors)
print('It is %f seconds long.' % tag.duration)
if image_data is not None:
    pi = Image.open(io.BytesIO(image_data))
    pi.show()
