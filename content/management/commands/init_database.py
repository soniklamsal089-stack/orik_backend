"""Initialize database with content only if empty.

This command is idempotent and safe to run on every deployment.
It only seeds content if the database is empty.
"""

from django.core.management.base import BaseCommand
from content.models import TeamMember, SiteSettings


class Command(BaseCommand):
    help = "Initialize database with content only if empty (safe for repeated deployments)"

    def handle(self, *args, **options):
        # Check if database already has content
        team_count = TeamMember.objects.count()
        site_exists = SiteSettings.objects.exists()
        
        self.stdout.write(f"Current state:")
        self.stdout.write(f"  - Team members: {team_count}")
        self.stdout.write(f"  - Site settings: {'exists' if site_exists else 'missing'}")
        
        if team_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Database already initialized with {team_count} team members."
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "  Skipping seed to preserve existing data (including admin edits)."
                )
            )
            return
        
        # Database is empty, seed it
        self.stdout.write(self.style.WARNING("Database is empty. Seeding initial content..."))
        
        from django.core.management import call_command
        call_command('seed_content', verbosity=self.verbosity)
        
        self.stdout.write(
            self.style.SUCCESS(
                "✓ Database initialized successfully. Content can now be edited via admin."
            )
        )
