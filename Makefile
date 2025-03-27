build:
	docker-compose build

up:
	docker-compose up -d

build_and_up:
	docker-compose build
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose down
	docker-compose up -d

clean_and_up:
	docker-compose down
	docker-compose build
	docker-compose up -d

migrate:
	docker-compose exec web sh -c "cd /app/APIHub && python manage.py migrate"

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

logs:
	docker-compose logs -f

shell:
	docker-compose exec web sh -c "cd /app/APIHub && python manage.py shell"
	
test:
	docker-compose exec web sh -c "cd /app/APIHub && python manage.py test"