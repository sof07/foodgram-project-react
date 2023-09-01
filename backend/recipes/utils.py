
import base64
from django.core.files.base import ContentFile
from PIL import Image
from collections import defaultdict


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


def generate_shopping_cart_csv(user):
    shopping_cart_entries = ShoppingCart.objects.filter(user=user)
    ingredient_totals = defaultdict(float)

    for entry in shopping_cart_entries:
        recipe = entry.recipe
        recipe_ingredients = recipe.recipe_ingredients.all()

        for ingredient_entry in recipe_ingredients:
            ingredient = ingredient_entry.ingredient
            amount_per_serving = ingredient_entry.amount
            total_amount = float(amount_per_serving)
            ingredient_totals[ingredient] += total_amount

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shopping_cart.csv"'

    writer = csv.writer(response)

    for ingredient, total_amount in ingredient_totals.items():
        writer.writerow([
            ingredient.name.capitalize(),
            total_amount,
            ingredient.measurement_unit
        ])

    return response
