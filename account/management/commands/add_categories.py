# your_app/management/commands/add_categories.py
from django.core.management.base import BaseCommand

from account.models import Category

class Command(BaseCommand):
    help = 'Add predefined categories to the Category model.'

    def handle(self, *args, **kwargs):
        # Predefined categories to add
        categories = [
            "ADULT MEMBER",
            "YOUTH MEMBER",
            "SENIOR MEMBER"
        ]

        for category_name in categories:
            # Check if category already exists
            if not Category.objects.filter(name=category_name).exists():
                # Create the category if it doesn't exist
                Category.objects.create(name=category_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully added category: {category_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category "{category_name}" already exists.'))
