"""
WSGI configuration for PythonAnywhere free hosting deployment.
To configure on PythonAnywhere:
1. In PythonAnywhere Web Tab, set 'Source code' to: /home/<your-username>/portfolio
2. Set 'Working directory' to: /home/<your-username>/portfolio
3. Set 'WSGI configuration file' to use the contents below (or link to this file).
4. Set 'Virtualenv' to: /home/<your-username>/.virtualenvs/portfolio-venv
5. Under 'Static files', add:
   URL: /static/      Directory: /home/<your-username>/portfolio/staticfiles
   URL: /media/       Directory: /home/<your-username>/portfolio/media
"""

import os
import sys

# Replace 'yourusername' with your actual PythonAnywhere username
username = os.environ.get('PA_USERNAME', 'yourusername')
project_home = f'/home/{username}/portfolio'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production on PythonAnywhere
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ.setdefault('DJANGO_DEBUG', 'False')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', f'127.0.0.1,localhost,{username}.pythonanywhere.com')

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
