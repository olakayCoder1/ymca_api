# your_app/management/commands/add_churches.py
from django.core.management.base import BaseCommand

from account.models import Church

class Command(BaseCommand):
    help = 'Add 10 predefined churches to the Church model.'

    def handle(self, *args, **kwargs):
        # Predefined churches to add
        churches = [
            "St. Mary's Church",
            "Grace Fellowship Church",
            "New Hope Church",
            "Good Shepherd Church",
            "City of Praise Church",
            "The Rock Church",
            "Living Water Church",
            "Victory Christian Church",
            "Redeemed Christian Church of God",
            "Bethel Church"
        ]

        for church_name in churches:
            # Check if the church already exists
            if not Church.objects.filter(name=church_name).exists():
                # Create the church if it doesn't exist
                Church.objects.create(name=church_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully added church: {church_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Church "{church_name}" already exists.'))
