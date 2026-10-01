release: python manage.py migrate && python manage.py seed_content --reset
web: gunicorn config.wsgi:application
