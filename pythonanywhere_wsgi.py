"""
WSGI configuration for PythonAnywhere free hosting deployment.
Domain: abhiramportfolio.pythonanywhere.com

To configure on PythonAnywhere:
1. In PythonAnywhere Web Tab, set 'Source code' to: /home/abhiramportfolio/portfolio
2. Set 'Working directory' to: /home/abhiramportfolio/portfolio
3. Set 'WSGI configuration file' to use the contents below (or link to this file).
4. Set 'Virtualenv' to: /home/abhiramportfolio/.virtualenvs/portfolio-venv
5. Under 'Static files', add:
   URL: /static/      Directory: /home/abhiramportfolio/portfolio/staticfiles
   URL: /media/       Directory: /home/abhiramportfolio/portfolio/media
"""

import os
import sys

# Default to abhiramportfolio or allow override via environment variable
username = os.environ.get('PA_USERNAME', 'abhiramportfolio')
project_home = f'/home/{username}/portfolio'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production on PythonAnywhere
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ.setdefault('DJANGO_DEBUG', 'False')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', f'127.0.0.1,localhost,{username}.pythonanywhere.com,.pythonanywhere.com')

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
