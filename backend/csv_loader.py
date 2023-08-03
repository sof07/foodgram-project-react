import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "grocery_assistant.settings")
django.setup()
from recipes.models import Ingredient
from users.models import CustomUser
import csv

def load_data_from_csv(csv_file_path):
    with open(csv_file_path, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # Пропустить заголовок CSV-файла
        for row in reader:
            name, measurement_unit = row
            ingredient = Ingredient.objects.create(
                name=name,
                measurement_unit=measurement_unit
            )
            print(f"Загружен ингредиент: {ingredient.name}")


if __name__ == "__main__":
    csv_file_path = os.path.join("..", "data", "ingredients.csv")
    load_data_from_csv(csv_file_path)
