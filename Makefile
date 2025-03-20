migrate:
	python manage.py migrate $(if $m, api $m,)

makemigrations:
	python manage.py makemigrations

createsuperuser:
	python manage.py createsuperuser

run:
	python manage.py runserver 127.0.0.1:8000

collectstatic:
	python manage.py collectstatic --no-input

dev:
	python manage.py runserver localhost:8000

command:
	python manage.py ${c}

shell:
	python manage.py shell

debug:
	python manage.py debug

venv:
    source venv/bin/activate
