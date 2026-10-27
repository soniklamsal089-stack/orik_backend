"""
Sync data from production API to local database.
Usage: python manage.py sync_from_api --api-url=https://orik-backend.onrender.com/api
"""
import requests
from django.core.management.base import BaseCommand
from content.models import Project, Testimonial, TeamMember, SiteSettings


class Command(BaseCommand):
    help = 'Sync data from production API to local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-url',
            type=str,
            default='https://orik-backend.onrender.com/api',
            help='Production API base URL'
        )

    def handle(self, *args, **options):
        api_url = options['api_url'].rstrip('/')
        
        try:
            # Fetch all content in one call
            self.stdout.write(self.style.SUCCESS('Fetching data from production API...'))
            response = requests.get(f'{api_url}/content/', timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Sync Site Settings
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Site Settings ==='))
            site_data = data.get('site', {})
            
            SiteSettings.objects.all().delete()
            SiteSettings.objects.create(
                site_name=site_data.get('site_name', 'Orik Webcraft'),
                tagline=site_data.get('tagline', ''),
                description=site_data.get('description', ''),
                email=site_data.get('email', ''),
                phone=site_data.get('phone', ''),
                whatsapp=site_data.get('whatsapp', ''),
                location=site_data.get('location', ''),
                address=site_data.get('address', ''),
                linkedin_url=site_data.get('linkedin_url', ''),
                facebook_url=site_data.get('facebook_url', ''),
                instagram_url=site_data.get('instagram_url', ''),
                twitter_url=site_data.get('twitter_url', ''),
                youtube_url=site_data.get('youtube_url', ''),
                github_url=site_data.get('github_url', '')
            )
            self.stdout.write(f'  ✓ Site: {site_data.get("site_name")}')
            self.stdout.write(f'  ✓ Email: {site_data.get("email")}')
            self.stdout.write(f'  ✓ Phone: {site_data.get("phone")}')

            # Sync Team Members
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Team Members ==='))
            team_data = data.get('team', [])
            
            TeamMember.objects.all().delete()
            team_count = 0
            for member in team_data:
                TeamMember.objects.create(
                    name=member['name'],
                    title=member['title'],
                    email=member.get('email', ''),
                    phone=member.get('phone', ''),
                    linkedin_url=member.get('linkedin_url', ''),
                    facebook_url=member.get('facebook_url', ''),
                    instagram_url=member.get('instagram_url', ''),
                    profile_image=member.get('profile_image', ''),
                    bio=member.get('bio', ''),
                    order=member.get('order', 0)
                )
                team_count += 1
                self.stdout.write(f'  ✓ {member["name"]} ({member["title"]})')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {team_count} team members'))

            # Sync Projects
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Projects ==='))
            project_data = data.get('projects', [])
            
            Project.objects.all().delete()
            project_count = 0
            for project in project_data:
                Project.objects.create(
                    title=project['title'],
                    slug=project['slug'],
                    client=project.get('client', ''),
                    category=project.get('category', ''),
                    icon=project.get('icon', ''),
                    description=project.get('description', ''),
                    features=project.get('features', ''),
                    long_description=project.get('long_description', ''),
                    year=project.get('year', 2024),
                    order=project.get('order', 0)
                )
                project_count += 1
                self.stdout.write(f'  ✓ {project["title"]}')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {project_count} projects'))

            # Sync Testimonials
            self.stdout.write(self.style.SUCCESS('\n=== Syncing Testimonials ==='))
            testimonial_data = data.get('testimonials', [])
            
            Testimonial.objects.all().delete()
            testimonial_count = 0
            for testimonial in testimonial_data:
                Testimonial.objects.create(
                    name=testimonial['name'],
                    title=testimonial.get('title', ''),
                    company=testimonial.get('company', ''),
                    avatar=testimonial.get('avatar', ''),
                    rating=testimonial.get('rating', 5),
                    message=testimonial.get('message', ''),
                    order=testimonial.get('order', 0)
                )
                testimonial_count += 1
                self.stdout.write(f'  ✓ {testimonial["name"]} - {testimonial.get("company", "N/A")}')
            
            self.stdout.write(self.style.SUCCESS(f'Synced {testimonial_count} testimonials'))

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully synced all data from production!\n'
                    f'   Team Members: {team_count}\n'
                    f'   Projects: {project_count}\n'
                    f'   Testimonials: {testimonial_count}\n'
                    f'   Site Settings: ✓'
                )
            )

        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching data from API: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing data: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
