#!/bin/bash

echo "Script starts"
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}"
until psql $DATABASE_URL -c '\l'; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 1
done
cd ./ProjSeeker
python manage.py makemigrations
python manage.py makemigrations portal
python manage.py migrate
python manage.py migrate portal
python manage.py create_groups
python manage.py create_superuser
# python manage.py crontab add
python manage.py collectstatic --noinput
#move to .env
echo "Starting WEB Server"
python -u manage.py runserver 0.0.0.0:8000
# echo "Script complete"
