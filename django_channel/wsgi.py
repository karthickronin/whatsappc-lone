import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_channel.settings')  # Ensure correct project name

application = get_wsgi_application()
