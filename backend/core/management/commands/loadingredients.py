import csv

from django.core.management.base import BaseCommand

from foods.models import Ingredient


class Command(BaseCommand):
    """Класс для команды скачивания ингредиентов"""

    help = 'Загрузка ингредиентов'

    def handle(self, *args, **kwargs):
        with open(
            './data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
        print('Ингредиенты добавлены в базу данных')
