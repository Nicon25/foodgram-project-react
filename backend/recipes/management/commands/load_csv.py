import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import (Ingredient)

TABLES = {
    Ingredient: 'ingredients.csv',
}

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    name = row[0]
                    measurement_unit = row[1]
                    model.objects.create(name=name, measurement_unit=measurement_unit)
        self.stdout.write(self.style.SUCCESS('Данные из CSV файла успешно загружены'))