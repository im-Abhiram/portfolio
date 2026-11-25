#!/bin/bash
# ==============================================================================
# PythonAnywhere One-Click Update Script
# Account: abhiramportfolio
# Domain: https://abhiramportfolio.pythonanywhere.com
# ==============================================================================
set -e

echo "=== [1/5] Navigating to portfolio directory ==="
cd /home/abhiramportfolio/portfolio

echo "=== [2/5] Activating virtual environment ==="
source /home/abhiramportfolio/.virtualenvs/portfolio-venv/bin/activate

echo "=== [3/5] Pulling latest updates from GitHub ==="
# Discard server-generated staticfiles modifications before pulling (collectstatic rebuilds them cleanly)
git checkout -- staticfiles/
git pull origin main

echo "=== [4/5] Installing dependencies & migrating database ==="
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

echo "=== [5/5] Reloading Web Application ==="
# Touching the WSGI file signals PythonAnywhere uWSGI workers to reload immediately
if [ -f /var/www/abhiramportfolio_pythonanywhere_com_wsgi.py ]; then
    touch /var/www/abhiramportfolio_pythonanywhere_com_wsgi.py
    echo "WSGI file touched successfully."
else
    echo "WSGI path /var/www/abhiramportfolio_pythonanywhere_com_wsgi.py not found. Please reload via Web tab."
fi

echo ""
echo "=============================================================================="
echo " [SUCCESS] Portfolio successfully updated!"
echo " Live site: https://abhiramportfolio.pythonanywhere.com"
echo " Operator:  https://abhiramportfolio.pythonanywhere.com/portal/login/"
echo "=============================================================================="
