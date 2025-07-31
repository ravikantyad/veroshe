from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Add default car part categories'

    def handle(self, *args, **kwargs):
        categories = [
            ('Engine Parts', 'engine-parts'),
            ('Lights & Electricals', 'lights-electricals'),
            ('Body Parts', 'body-parts'),
            ('Interiors', 'interiors'),
            ('Wheels & Tyres', 'wheels-tyres'),
            ('Brakes', 'brakes'),
            ('Suspension', 'suspension'),
            ('Exhaust', 'exhaust'),
            ('Transmission', 'transmission'),
        ]

        for name, slug in categories:
            Category.objects.get_or_create(name=name, slug=slug)
        
        self.stdout.write(self.style.SUCCESS('Categories added successfully!'))
