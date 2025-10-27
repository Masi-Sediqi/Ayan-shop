#!/usr/bin/env bash
set -o errexit  # exit on error

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🧱 Running collectstatic..."
python manage.py collectstatic --no-input

echo "🗃️ Applying database migrations..."
python manage.py makemigrations
echo "🗃️ Applying database migrate..."
python manage.py migrate

if [[ $CREATE_SUPERUSER == "True" ]]; then
  echo "👤 Creating superuser..."
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    User.objects.create_superuser("${DJANGO_SUPERUSER_USERNAME}", "${DJANGO_SUPERUSER_EMAIL}", "${DJANGO_SUPERUSER_PASSWORD}")
EOF
else
  echo "Skipping superuser creation"
fi

echo "✅ Build complete!"
