
import base64
from django.core.files.base import ContentFile
from PIL import Image


def base64_to_image(data):
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    image_data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
    return image_data


def to_internal_value(self, data):
    from django.core.files.base import ContentFile
    import base64
    import six
    import uuid

    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            self.fail('invalid_image')

        # Generate file name:
        # 12 characters are more than enough.
        file_name = str(uuid.uuid4())[:12]
        # Get the file name extension:
        file_extension = self.get_file_extension(file_name, decoded_file)

        complete_file_name = "%s.%s" % (file_name, file_extension, )

        data = ContentFile(decoded_file, name=complete_file_name)

    return super(Base64ImageField, self).to_internal_value(data)


def get_file_extension(self, file_name, decoded_file):
    import imghdr

    extension = imghdr.what(file_name, decoded_file)
    extension = "jpg" if extension == "jpeg" else extension

    return extension
