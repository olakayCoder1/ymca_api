import random
from datetime import date
from django.core.management.base import BaseCommand
from account.models import IDCard


class Command(BaseCommand):
    help = 'Update existing ID numbers to match the new LYA/LYY pattern based on user age'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all ID cards
        id_cards = IDCard.objects.select_related('user__user_request').all()
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        self.stdout.write(self.style.SUCCESS(f'Processing {id_cards.count()} ID cards...'))
        
        for card in id_cards:
            # Check if ID already matches the pattern (LYA or LYY followed by 7 digits)
            if card.id_number and (
                (card.id_number.startswith('LYA') and len(card.id_number) == 10 and card.id_number[3:].isdigit()) or
                (card.id_number.startswith('LYY') and len(card.id_number) == 10 and card.id_number[3:].isdigit())
            ):
                skipped_count += 1
                continue
            
            try:
                # Get user's age from date_of_birth if available
                age = None
                if card.user.user_request and card.user.user_request.date_of_birth:
                    dob = card.user.user_request.date_of_birth
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                
                # Determine prefix based on age
                if age is not None and age >= 31:
                    prefix = 'LYA'
                else:
                    prefix = 'LYY'
                
                # Generate new ID number
                random_digits = str(random.randint(1000000, 9999999))
                new_id_number = f'{prefix}{random_digits}'
                
                old_id = card.id_number
                
                if dry_run:
                    self.stdout.write(
                        f'Would update: {card.user.email} - '
                        f'Old: {old_id} -> New: {new_id_number} '
                        f'(Age: {age if age else "Unknown"})'
                    )
                else:
                    card.id_number = new_id_number
                    card.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated: {card.user.email} - '
                            f'Old: {old_id} -> New: {new_id_number} '
                            f'(Age: {age if age else "Unknown"})'
                        )
                    )
                
                updated_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error updating card for {card.user.email}: {str(e)}'
                    )
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n--- Summary ---'))
        self.stdout.write(f'Total ID cards processed: {id_cards.count()}')
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped (already valid): {skipped_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nThis was a dry run. No changes were made. '
                    'Run without --dry-run to apply changes.'
                )
            )
