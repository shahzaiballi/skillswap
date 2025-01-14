# core/management/commands/setup_dummy_data.py
from django.core.management.base import BaseCommand
from core.models import User, Category, Skill
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Creates dummy data for testing'

    def handle(self, *args, **kwargs):
        # Create dummy users
        users = [
            {
                'username': 'learner@example.com',
                'email': 'learner@example.com',
                'password': make_password('learner123'),
                'role': 'LEARNER',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            {
                'username': 'sharer1@example.com',
                'email': 'sharer1@example.com',
                'password': make_password('sharer123'),
                'role': 'SKILL_SHARER',
                'first_name': 'Jane',
                'last_name': 'Smith'
            },
            {
                'username': 'sharer2@example.com',
                'email': 'sharer2@example.com',
                'password': make_password('sharer456'),
                'role': 'SKILL_SHARER',
                'first_name': 'Mike',
                'last_name': 'Johnson'
            }
        ]

        for user_data in users:
            User.objects.create(**user_data)

        # Create categories
        categories = ['Programming', 'Languages', 'Music', 'Art', 'Fitness']
        for cat_name in categories:
            Category.objects.create(
                name=cat_name,
                description=f'Learn and share skills related to {cat_name}'
            )

        self.stdout.write(self.style.SUCCESS('Successfully created dummy data'))