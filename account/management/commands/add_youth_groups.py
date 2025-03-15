# your_app/management/commands/add_youth_groups.py
from django.core.management.base import BaseCommand

from account.models import YouthGroup

class Command(BaseCommand):
    help = 'Add predefined youth groups to the YouthGroup model.'

    def handle(self, *args, **kwargs):
        # Predefined youth groups to add
        youth_groups = [
            "Hi-Y",
            "Y-Elite",
            "Young Leaders Program",
            "Future Leaders Fellowship",
            "Youth for Change",
            "Leadership Academy",
            "Teen Ambassadors",
            "Young Achievers",
            "Youth Empowerment",
            "Hope for the Future"
        ]

        for group_name in youth_groups:
            # Check if the youth group already exists
            if not YouthGroup.objects.filter(name=group_name).exists():
                # Create the youth group if it doesn't exist
                YouthGroup.objects.create(name=group_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully added youth group: {group_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Youth group "{group_name}" already exists.'))
