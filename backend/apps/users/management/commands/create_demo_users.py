"""
Management command: create demo users for WariMitra testing.

Usage: python manage.py create_demo_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEMO_USERS = [
    {'username': 'pilgrim_1', 'password': 'Pilgrim@123', 'role': 'PILGRIM', 'first_name': 'Anish', 'last_name': 'Jadhav', 'mobile': '9876543210'},
    {'username': 'volunteer_1', 'password': 'Volunteer@123', 'role': 'VOLUNTEER', 'first_name': 'Priya', 'last_name': 'Sharma', 'mobile': '9876543211'},
    {'username': 'dindi_leader', 'password': 'Dindi@Leader1', 'role': 'DINDI_LEADER', 'first_name': 'Ramesh', 'last_name': 'Patil', 'mobile': '9876543212'},
    {'username': 'medical_officer', 'password': 'MedOfficer@123', 'role': 'MEDICAL_STAFF', 'first_name': 'Dr. Sneha', 'last_name': 'Kulkarni', 'mobile': '9876543213'},
    {'username': 'police_officer', 'password': 'Police@1234', 'role': 'POLICE_OFFICER', 'first_name': 'Sub-Inspector', 'last_name': 'Desai', 'mobile': '9876543214'},
    {'username': 'ngo_coord', 'password': 'NGO@123456', 'role': 'NGO_COORDINATOR', 'first_name': 'Kavita', 'last_name': 'More', 'mobile': '9876543215'},
    {'username': 'admin', 'password': 'Admin@12345', 'role': 'ADMIN', 'first_name': 'Admin', 'last_name': 'User', 'mobile': '9876543216', 'is_staff': True, 'is_superuser': True},
]


class Command(BaseCommand):
    help = 'Create demo users for WariMitra development and testing'

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in DEMO_USERS:
            is_staff = data.pop('is_staff', False)
            is_superuser = data.pop('is_superuser', False)
            password = data.pop('password')

            user, created_now = User.objects.update_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'is_verified': True,
                }
            )
            user.set_password(password)
            user.save()

            if created_now:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {user.username} ({user.role})'))
            else:
                updated += 1
                self.stdout.write(f'  Updated: {user.username} ({user.role})')

        self.stdout.write(self.style.SUCCESS(f'\nDone: {created} created, {updated} updated.'))
        self.stdout.write('')
        self.stdout.write('Test credentials:')
        for data in DEMO_USERS:
            self.stdout.write(f'  {data["username"]} / (as in code)')
