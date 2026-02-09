from django.core.management.base import BaseCommand
from apps.accounts.models import Player


class Command(BaseCommand):
    help = 'Creates an admin user with a unique code for login'

    def handle(self, *args, **options):
        # Check if admin already exists
        admin_email = 'admin@nbcc.com'
        
        if Player.objects.filter(email=admin_email).exists():
            admin = Player.objects.get(email=admin_email)
            self.stdout.write(
                self.style.WARNING(f'Admin user already exists!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {admin.email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Admin Code: {admin.unique_code}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Name: {admin.name}')
            )
            return

        # Create admin user
        admin = Player.objects.create_superuser(
            email=admin_email,
            name='Admin User',
            password='admin123',  # Default password (can be changed later)
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created admin user!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Email: {admin.email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Admin Code: {admin.unique_code}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Name: {admin.name}')
        )
        self.stdout.write(
            self.style.WARNING(f'Password: admin123 (change this in production!)')
        )
