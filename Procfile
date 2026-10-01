release: python manage.py migrate && python manage.py seed_content --reset && python manage.py collectstatic --noinput
web: gunicorn config.wsgi:application
