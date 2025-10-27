@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Collecting static files...
python manage.py collectstatic --no-input

echo Running migrations...
python manage.py migrate

if "%CREATE_SUPERUSER%"=="True" (
    echo Creating superuser...
    python manage.py createsuperuser --no-input --email "%DJANGO_SUPERUSER_EMAIL%"
)

echo Done!
