"""
Sync data from production database to local database.
Usage: python manage.py sync_from_production
"""
import os
import django
from django.core.management.base import BaseCommand
from django.db import connections
from psycopg2 import connect
from content.models import Project, Testimonial, TeamMember, SiteSettings


class Command(BaseCommand):
    help = 'Sync data from production PostgreSQL to local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--production-url',
            type=str,
            help='Production DATABASE_URL (PostgreSQL connection string)',
            default=os.environ.get('PRODUCTION_DATABASE_URL', '')
        )

    def handle(self, *args, **options):
        production_url = options['production_url']
        
        if not production_url:
            self.stdout.write(
                self.style.ERROR(
                    'Please provide production database URL:\n'
                    'python manage.py sync_from_production --production-url="postgresql://..."\n'
                    'Or set PRODUCTION_DATABASE_URL environment variable'
                )
            )
            return

        try:
            # Connect to production database with SSL
            self.stdout.write('Connecting to production database...')
            
            # Parse connection string and add SSL requirement
            import ssl
            prod_conn = connect(production_url, sslmode='require')
            prod_cursor = prod_conn.cursor()

            # Sync TeamMembers
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Team Members ==='))
            prod_cursor.execute("""
                SELECT id, name, title, email, phone, linkedin_url, facebook_url, 
                       instagram_url, profile_image, bio, "order", created_at, updated_at
                FROM content_teammember
                ORDER BY "order", id
            """)
            
            TeamMember.objects.all().delete()
            team_count = 0
            for row in prod_cursor.fetchall():
                TeamMember.objects.create(
                    id=row[0],
                    name=row[1],
                    title=row[2],
                    email=row[3],
                    phone=row[4],
                    linkedin_url=row[5],
                    facebook_url=row[6],
                    instagram_url=row[7],
                    profile_image=row[8],
                    bio=row[9],
                    order=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )
                team_count += 1
                self.stdout.write(f'  ✓ {row[1]} ({row[2]})')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {team_count} team members'))

            # Sync Site Settings
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Site Settings ==='))
            prod_cursor.execute("""
                SELECT id, site_name, tagline, description, email, phone, 
                       whatsapp, location, address, linkedin_url, facebook_url, 
                       instagram_url, twitter_url, youtube_url, github_url, 
                       updated_at
                FROM content_sitesettings
                LIMIT 1
            """)
            
            site_row = prod_cursor.fetchone()
            if site_row:
                SiteSettings.objects.all().delete()
                SiteSettings.objects.create(
                    id=site_row[0],
                    site_name=site_row[1],
                    tagline=site_row[2],
                    description=site_row[3],
                    email=site_row[4],
                    phone=site_row[5],
                    whatsapp=site_row[6],
                    location=site_row[7],
                    address=site_row[8],
                    linkedin_url=site_row[9],
                    facebook_url=site_row[10],
                    instagram_url=site_row[11],
                    twitter_url=site_row[12],
                    youtube_url=site_row[13],
                    github_url=site_row[14],
                    updated_at=site_row[15]
                )
                self.stdout.write(f'  ✓ Site: {site_row[1]}')
                self.stdout.write(f'  ✓ Email: {site_row[4]}')
                self.stdout.write(f'  ✓ Phone: {site_row[5]}')
                self.stdout.write(self.style.SUCCESS('Synced site settings'))

            # Sync Projects
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Projects ==='))
            prod_cursor.execute("""
                SELECT id, title, slug, client, category, icon, description, 
                       features, long_description, year, "order", created_at, updated_at
                FROM content_project
                ORDER BY "order", id
            """)
            
            Project.objects.all().delete()
            project_count = 0
            for row in prod_cursor.fetchall():
                Project.objects.create(
                    id=row[0],
                    title=row[1],
                    slug=row[2],
                    client=row[3],
                    category=row[4],
                    icon=row[5],
                    description=row[6],
                    features=row[7],
                    long_description=row[8],
                    year=row[9],
                    order=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )
                project_count += 1
                self.stdout.write(f'  ✓ {row[1]}')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {project_count} projects'))

            # Sync Testimonials
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Testimonials ==='))
            prod_cursor.execute("""
                SELECT id, name, title, company, avatar, rating, message, 
                       "order", created_at, updated_at
                FROM content_testimonial
                ORDER BY "order", id
            """)
            
            Testimonial.objects.all().delete()
            testimonial_count = 0
            for row in prod_cursor.fetchall():
                Testimonial.objects.create(
                    id=row[0],
                    name=row[1],
                    title=row[2],
                    company=row[3],
                    avatar=row[4],
                    rating=row[5],
                    message=row[6],
                    order=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )
                testimonial_count += 1
                self.stdout.write(f'  ✓ {row[1]} - {row[3]}')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {testimonial_count} testimonials'))

            # Close connection
            prod_cursor.close()
            prod_conn.close()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully synced all data from production!\n'
                    f'   Team Members: {team_count}\n'
                    f'   Projects: {project_count}\n'
                    f'   Testimonials: {testimonial_count}\n'
                    f'   Site Settings: ✓'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing data: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
