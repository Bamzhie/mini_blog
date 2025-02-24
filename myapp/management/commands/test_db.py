# myapp/management/commands/test_db.py
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Test the database connection"

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(
                        self.style.SUCCESS("Database connection successful")
                    )
                else:
                    self.stdout.write(self.style.ERROR("Database connection failed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database connection failed: {e}"))
