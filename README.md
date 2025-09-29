# Transit Backend
OAuth2 + MFA, Google Maps live ingestion, DynamoDB, GA scheduler.

## Quick start
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Env
Copy `.env.example` to `.env` and fill real values.
