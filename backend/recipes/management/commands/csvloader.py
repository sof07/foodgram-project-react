import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузить ингредиенты из файла CSV'

    def handle(self, *args, **options):
        # Жестко указываем путь к файлу CSV
        csv_file_path = os.path.join(os.getcwd(), 'data', 'ingredients.csv')

        if not os.path.exists(csv_file_path):
            self.stderr.write(self.style.ERROR(
                'Файл CSV не найден. Укажите правильный путь.'))
            return

        with open(csv_file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Пропустить заголовок CSV-файла
            for row in reader:
                name, measurement_unit = row
                ingredient = Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Загружен ингредиент: {ingredient.name}'))
